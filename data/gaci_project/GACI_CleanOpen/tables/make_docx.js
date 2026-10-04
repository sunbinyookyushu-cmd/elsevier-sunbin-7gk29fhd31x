// Build results_tables.docx from _tables.json (landscape A4, one table per section)
const fs = require("fs");
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, AlignmentType, BorderStyle, PageOrientation, HeadingLevel, ShadingType, PageBreak } = require("docx");
const tables = JSON.parse(fs.readFileSync(__dirname + "/_tables.json", "utf8"));
const clean = s => String(s).replace(/\$\\times\$/g, "×").replace(/\$\^2\$/g, "²").replace(/\\%/g, "%").replace(/\$/g, "").replace(/--/g, "–").replace(/\\/g, "");
const PAGE_W = 15840 - 2 * 1080;   // landscape A4-ish width minus margins (DXA)
const none = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const thin = { style: BorderStyle.SINGLE, size: 6, color: "000000" };
function cell(text, w, opts = {}) {
  return new TableCell({
    width: { size: w, type: WidthType.DXA },
    borders: { top: opts.top || none, bottom: opts.bottom || none, left: none, right: none },
    margins: { top: 40, bottom: 40, left: 60, right: 60 },
    children: [new Paragraph({ alignment: opts.align || AlignmentType.CENTER, children: [new TextRun({ text: clean(text), size: 17, font: "Times New Roman", bold: !!opts.bold, italics: !!opts.italics })] })],
  });
}
const children = [];
children.push(new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun({ text: "Is air connectivity clean connectivity? Core results", font: "Times New Roman" })] }));
children.push(new Paragraph({ children: [new TextRun({ text: "Unified sample: 149 countries, 1996–2019 (country-years with all Table 1 outcomes and both instruments observed; 3,425 observations). Dependent variables: CEDS SO2 and NOx, WDI renewable share, OWID/EI CO2 and energy. Air connectivity = log of the seat-weighted mean GACI of a country's airports. All regressions include country and year fixed effects, ln population, ln GDP per capita and its square; standard errors clustered by country.", size: 20, font: "Times New Roman" })] }));
for (const t of tables) {
  const isMain = t.name.startsWith("T");
  const ncol = t.cols.length; const labW = Math.min(4200, Math.round(PAGE_W * 0.28)); const colW = Math.floor((PAGE_W - labW) / ncol);
  children.push(new Paragraph({ pageBreakBefore: true, heading: HeadingLevel.HEADING_2, children: [new TextRun({ text: `${isMain ? "Table " + t.name.slice(1) : "Appendix Table " + t.name.slice(1)}. ${clean(t.title)}`, font: "Times New Roman" })] }));
  const rows = [];
  rows.push(new TableRow({ tableHeader: true, children: [cell("", labW, { top: thin, bottom: thin }), ...t.cols.map(c => cell(c, colW, { top: thin, bottom: thin, bold: true }))] }));
  const nObsIdx = t.rows.findIndex(r => r[0] === "Observations");
  t.rows.forEach((r, i) => {
    const isLast = i === t.rows.length - 1; const topLine = i === nObsIdx;
    const lab = r[0]; const vals = r[1];
    rows.push(new TableRow({ children: [cell(lab, labW, { align: AlignmentType.LEFT, top: topLine ? thin : none, bottom: isLast ? thin : none, italics: lab.startsWith("    ") }), ...vals.map(v => cell(v, colW, { top: topLine ? thin : none, bottom: isLast ? thin : none }))] }));
  });
  children.push(new Table({ width: { size: labW + colW * ncol, type: WidthType.DXA }, columnWidths: [labW, ...Array(ncol).fill(colW)], rows }));
  children.push(new Paragraph({ spacing: { before: 120 }, children: [new TextRun({ text: "Notes: " + clean(t.note), size: 16, font: "Times New Roman" })] }));
}
const doc = new Document({
  styles: { default: { document: { run: { font: "Times New Roman", size: 20 } } } },
  sections: [{ properties: { page: { size: { width: 11906, height: 16838, orientation: PageOrientation.LANDSCAPE }, margin: { top: 1080, bottom: 1080, left: 1080, right: 1080 } } }, children }],
});
Packer.toBuffer(doc).then(b => { fs.writeFileSync(__dirname + "/results_tables.docx", b); console.log("written results_tables.docx"); });

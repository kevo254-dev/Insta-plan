import streamlit as st
import datetime, urllib.parse

st.set_page_config(page_title='InstantPlan Demo', layout='centered')
st.title('InstantPlan — AI Building Plan Approval (Demo)')
st.markdown('**Group:** Kelvin (AI/ML) & Margaret Waithera Wambui (MERN)')
st.markdown('**SDG alignment:** SDG 11 — Sustainable Cities and Communities')

st.header('Upload a Building Plan (mock)')
uploaded = st.file_uploader('Upload a building plan (image or PDF)', type=['pdf','png','jpg','jpeg'])

def mock_ocr(file_bytes):
    # very naive mock OCR: return fixed sample text that includes registration IDs
    return """Architect: John Doe\nBORAQS Reg: A-12345\nEngineer: Jane Smith\nEBK Reg: E-67890\nNotes: Site plan, structural drawings included."""

def mock_ml_analysis(extracted_text):
    # mock feature extraction and scoring
    issues = []
    text = extracted_text.lower()
    score = 0.8
    if 'site plan' not in text:
        issues.append('missing_site_plan')
        score -= 0.2
    if 'structural' not in text:
        issues.append('missing_structural_drawings')
        score -= 0.3
    return { 'approval_probability': round(max(0, score),3), 'issues': issues, 'extracted_text': extracted_text }

def mock_verify(reg_type, reg_id):
    # simple rule: BORAQS pass if contains 'A', EBK pass if contains 'E'
    present = ('a' in reg_id.lower()) if reg_type=='boraqs' else ('e' in reg_id.lower())
    return { 'present': present, 'reg_type': reg_type, 'reg_id': reg_id, 'checked_at': datetime.datetime.utcnow().isoformat()+'Z' }

if uploaded:
    st.success('File received (demo). Running mock OCR and analysis...')
    bytes_data = uploaded.read()
    extracted = mock_ocr(bytes_data)
    st.subheader('Extracted (mock) OCR text')
    st.code(extracted)
    st.subheader('AI Analysis (mock)')
    analysis = mock_ml_analysis(extracted)
    st.json(analysis)
    # extract reg ids (very naive)
    boraqs_id = ''
    ebk_id = ''
    for line in extracted.splitlines():
        if 'boraqs' in line.lower():
            boraqs_id = line.split(':')[-1].strip()
        if 'ebk' in line.lower():
            ebk_id = line.split(':')[-1].strip()
    st.subheader('Professional Verification (mock)')
    bres = mock_verify('boraqs', boraqs_id or 'A-XXXXX')
    eres = mock_verify('ebk', ebk_id or 'E-YYYYY')
    st.write('BORAQS verification:', bres)
    st.write('EBK verification:', eres)
    st.header('Approval Flow')
    st.write('Approval probability:', analysis['approval_probability'])
    pay = st.button('Simulate MPESA Payment (mock)')
    if pay:
        st.success('Payment simulated — marking as paid.')
        paid = True
    else:
        paid = False
    if analysis['approval_probability'] >= 0.75 and (paid or st.checkbox('Force mark as paid (demo)')):
        approval_id = 'APPR-' + datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')
        st.success(f'Plan APPROVED — Approval ID: {approval_id}')
        verify_url = f"https://example.com/verify-plan/{approval_id}"
        qr_url = 'https://chart.googleapis.com/chart?cht=qr&chs=300x300&chl=' + urllib.parse.quote(verify_url)
        st.image(qr_url, width=200)
        st.markdown(f'**Verification link:** {verify_url}')
        if st.button('Download Approval Certificate (PDF)'):
            # create a simple PDF bytes for download (very minimal)
            from io import BytesIO
            def create_simple_pdf(text):
                # minimal PDF generator (very small); for full features use reportlab
                lines = text.splitlines()
                content_lines = []
                y = 750
                for line in lines:
                    safe = line.replace('(', '\(').replace(')', '\)')
                    content_lines.append(f"BT /F1 12 Tf 50 {y} Td ({safe}) Tj ET")
                    y -= 14
                    if y < 50:
                        break
                content = "\n".join(content_lines)
                objs = []
                objs.append("%PDF-1.4\n")
                objs.append("1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")
                objs.append("2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n")
                objs.append("3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>\nendobj\n")
                objs.append("4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n")
                objs.append(f"5 0 obj\n<< /Length {len(content.encode('utf-8'))} >>\nstream\n{content}\nendstream\nendobj\n")
                return "".join(objs).encode('utf-8')
            pdf_text = f"InstantPlan Approval Certificate\nApproval ID: {approval_id}\nOwner: (demo)\nDate: {datetime.datetime.utcnow().isoformat()}\nSDG: SDG 11 - Sustainable Cities and Communities\n\nVerification: {verify_url}\n"
            pdf_bytes = create_simple_pdf(pdf_text)
            st.download_button('Download PDF', data=pdf_bytes, file_name=f'approval_{approval_id}.pdf', mime='application/pdf')
    else:
        st.warning('Plan not approved automatically. Resolve issues or force approve.')
else:
    st.info('Upload a sample plan to see the demo flow. (This is a demo — not connected to real registries.)')

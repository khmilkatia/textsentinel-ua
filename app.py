import streamlit as st

from textsentinel import analyze
from textsentinel.cli import fix_text

st.set_page_config(page_title="textsentinel", page_icon="🪶")
st.title("🪶 textsentinel")
st.caption("Перевірка якості тексту: пробіли, пунктуація, повтори")

text = st.text_area("Вставте текст", height=250)
uploaded = st.file_uploader("або завантажте файл .txt", type=["txt"])
if uploaded:
    text = uploaded.read().decode("utf-8-sig")

col_a, col_b = st.columns(2)
check = col_a.button("Перевірити")
fix = col_b.button("Виправити")

if check and text.strip():
    report = analyze(text)

    col1, col2, col3 = st.columns(3)
    col1.metric("Оцінка якості", f"{report.score}/100")
    col2.metric("Слів", report.stats["words"])
    col3.metric("Проблем", report.summary["total"])

    if report.issues:
        st.subheader("Знахідки")
        st.dataframe([
            {"Рядок": i.line, "Колонка": i.column, "Правило": i.rule,
             "Серйозність": i.severity, "Опис": i.message,
             "Пропозиція": i.suggestion or ""}
            for i in report.issues
        ])
    else:
        st.success("Проблем не знайдено")

if fix and text.strip():
    fixed = fix_text(text)
    st.subheader("Виправлений текст")
    st.text_area("Результат", fixed, height=250)
    st.download_button("Завантажити clean.txt", fixed, file_name="clean.txt")

    remaining = analyze(fixed)
    st.subheader("Що лишилося виправити вручну")
    if remaining.issues:
        st.dataframe([
            {"Рядок": i.line, "Колонка": i.column, "Правило": i.rule,
             "Опис": i.message}
            for i in remaining.issues
        ])
    else:
        st.success("Усе виправлено")
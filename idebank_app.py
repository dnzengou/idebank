import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
import pandas as pd

SCOPE = "https://www.googleapis.com/auth/spreadsheets"
SPREADSHEET_ID = "1coKcUQWYzuO6gvKIjIpLO_6JbNz33kJpIP0daWIL2AI"
SHEET_NAME = "Idebank"
GSHEET_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}"


@st.experimental_singleton()
def connect_to_gsheet():
    # Create a connection object.
    credentials = service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=[SCOPE],
    )

    service = build("sheets", "v4", credentials=credentials)
    gsheet_connector = service.spreadsheets()
    return gsheet_connector


def get_data(gsheet_connector) -> pd.DataFrame:
    values = (
        gsheet_connector.values()
        .get(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{SHEET_NAME}!A:E",
        )
        .execute()
    )

    df = pd.DataFrame(values["values"])
    df.columns = df.iloc[0]
    df = df[1:]
    return df


def add_row_to_gsheet(gsheet_connector, row) -> None:
    values = (
        gsheet_connector.values()
        .append(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{SHEET_NAME}!A:E",
            body=dict(values=row),
            valueInputOption="USER_ENTERED",
        )
        .execute()
    )


st.set_page_config(page_title="Idébank", page_icon="💡", layout="centered")

st.title("🗳️💡 Idébank")

gsheet_connector = connect_to_gsheet()

st.sidebar.write(
    f"Denna app ska användas för att samla in idéer från SU Center of Digital Hälsa-teamet, lagra dem på ett [Google Sheet]({GSHEET_URL})  sorterat efter kategori och prioritetsnivå."
)

st.sidebar.write(
    f"[Read more](https://docs.streamlit.io/knowledge-base/tutorials/databases/public-gsheet) about connecting your Streamlit app to Google Sheets."
)

form = st.form(key="annotation")

with form:
    cols = st.columns((1, 1))
    author = cols[0].text_input("Report author:")
    idea_category = cols[1].selectbox(
        "Idékategori:", ["Innovation", "Visualisering", "Finansiering", "Utbildning", "API", "Problelösning", "Utvekling", "Nätverka", "RPA", "IoT lab", "AR VR"], index=2
    )
    description = st.text_area("Beskrivning:")
    cols = st.columns(2)
    date = cols[0].date_input("Idéns inlämningsdatum:")
    idea_priority = cols[1].slider("Ide proritet:", 0, 1, 2, 3)
    submitted = st.form_submit_button(label="Skicka in")


if submitted:
    add_row_to_gsheet(
        gsheet_connector, [[author, idea_category, description, str(date), idea_priority]]
    )
    st.success("Jaaaj 🎉 Din idé har sparats!")
    st.balloons()

expander = st.expander("Se alla resultat")
with expander:
    st.write(f"Öppna originalet [Google Sheet]({GSHEET_URL})")
    st.dataframe(get_data(gsheet_connector))

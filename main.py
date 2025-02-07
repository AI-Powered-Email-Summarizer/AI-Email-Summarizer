import streamlit as st
from email_fetcher import fetch_unread_emails

st.title("📩 AI Email Summarizer")
st.write("Fetch & summarize your unread emails automatically!")

if st.button("Fetch Emails"):
    st.write("Fetching emails... (Coming soon!)")
    emails = fetch_unread_emails()

    if not emails:
        st.warning("No unread emails found! 🎉")
    else:
        for email in emails:
            with st.expander(f"📧 {email['subject']}"):
                st.write(f"**From:** {email['sender']}")
                st.write(f"**Snippet:** {email['snippet']}")

import streamlit as st
from work_email import fetch_emails, classify_email

st.title("📩 AI Email Summarizer")
st.write("Fetch & summarize your unread emails automatically!")

if st.button("Fetch Emails"):
    st.write("📩 Fetching emails...")
    emails = fetch_emails()

    if not emails:
        st.success("No unread emails found! 🎉")
    else:
        important_emails = [email for email in emails if classify_email(email["subject"]) == "Important"]
        other_emails = [email for email in emails if classify_email(email["subject"]) == "Other"]

        st.subheader("🔥 Important Emails")
        for email in important_emails:
            with st.expander(f"📧 {email['subject']}"):
                st.write(f"**From:** {email['sender']}")
                st.write(f"**Snippet:** {email['snippet']}")
                st.write(f"**Summary:** {(email['summary'])}")

        st.subheader("📂 Other Emails")
        for email in other_emails:
            with st.expander(f"📧 {email['subject']}"):
                st.write(f"**From:** {email['sender']}")
                st.write(f"**Snippet:** {email['snippet']}")

import streamlit as st
st.title("demo app")
name = st.text_input("enter you name")
if st.button("hey hello"):
    if name:
        st.success(f"hello {name}, welcome")
    else:
        st.warning("plz enter name")
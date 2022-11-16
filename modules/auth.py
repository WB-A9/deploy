import streamlit as st

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["WBA9"]["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "비밀번호", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "비밀번호", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 비밀번호가 틀렸습니다.")
        return False
    else:
        # Password correct.
        return True

def signout():
    def signout_pressed():
        del st.session_state["password_correct"]
        
    st.button("Sign out", on_click = signout_pressed)
    
    
        


import streamlit as st
import os

def get_page_files(directory="pages"):
    """Return a list of .py files in the given directory."""
    page_files = []
    for file in os.listdir(directory):
        if file.endswith(".py"):
            page_files.append(file)
    return sorted(page_files)

def get_page_display_name(page_file):
    """Return a readable page name from the file name."""
    name = page_file.replace("_", " ").replace(".py", "")
    return name.title()

def run_page(page_file, directory="pages"):
    """Run the Python file in the given directory."""
    page_path = os.path.join(directory, page_file)
    with open(page_path, "r", encoding="utf-8") as file:
        code = file.read()
        exec(code, globals())

def main():
    st.set_page_config(page_title="Heritage-All Forms", layout="wide")
    st.title("Heritage Survey - All Pages")

    # Get list of page files from the 'pages' directory
    page_files = get_page_files("pages")
    if not page_files:
        st.warning("No pages found in the 'pages' directory.")
        return

    # Sidebar for page selection
    page_name_map = {get_page_display_name(f): f for f in page_files}
    page_names = list(page_name_map.keys())

    selected_page = st.sidebar.selectbox("Select a page", page_names)

    st.header(selected_page)
    run_page(page_name_map[selected_page], "pages")

if __name__ == "__main__":
    main()

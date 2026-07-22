import os

def load_css(css_file):
    with open(css_file) as f:
        return f.read()


def create_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)

def save_upload_file(uploaded_file, destination):
    filepath = os.path.join(destination, uploaded_file.name)
    with open(filepath, "wb") as f:
         f.write(uploaded_file.getbuffer())
    return filepath


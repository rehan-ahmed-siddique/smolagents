"""
Smolagents: Smart AI Assistant with Live Image + Web Search (Streamlit)
Generates an image or searches for info depending on query.
"""

import streamlit as st
from smolagents import load_tool, DuckDuckGoSearchTool, HfApiModel
import base64

# Load tools
image_tool = load_tool(
    "m-ric/text-to-image", 
    trust_remote_code=True, 
    name="image_generator"
)
search_tool = DuckDuckGoSearchTool()

# Load model
model = HfApiModel("Qwen/Qwen2.5-72B-Instruct")

# Save image in memory
def display_image(b64_string):
    data = base64.b64decode(b64_string)
    st.image(data, use_column_width=True)

# Decide if query is image-related
def is_image_query(prompt: str) -> bool:
    keywords = ["draw", "picture", "photo", "image", "painting", "art", "render", "generate", "illustration"]
    return any(k in prompt.lower() for k in keywords)

# UI
st.title("🖼 Smolagents AI Assistant")
query = st.text_input("Enter your query:")

if st.button("Run"):
    if is_image_query(query):
        st.subheader("Generating Image...")
        image_result = image_tool(query)
        if isinstance(image_result, dict) and "image" in image_result:
            display_image(image_result["image"])
        else:
            st.error("Could not generate image.")
        st.subheader("Related Web Search Results")
        info = search_tool(query)
        st.write(info)
    else:
        st.subheader("Searching for Information...")
        info = search_tool(query)
        st.write(info)

import streamlit as st
import base64

# Handle imports with better error messages
try:
    from smolagents import load_tool, DuckDuckGoSearchTool, InferenceClientModel
except ImportError as e:
    st.error(f"Smolagents import error: {e}")
    st.info("Make sure to install: pip install smolagents ddgs")
    st.stop()

# Initialize tools and model with error handling
@st.cache_resource
def initialize_tools():
    try:
        # Load tools
        image_tool = load_tool(
            "m-ric/text-to-image",
            trust_remote_code=True,
            name="image_generator"
        )
        search_tool = DuckDuckGoSearchTool()
        model = InferenceClientModel("Qwen/Qwen2.5-72B-Instruct")
        return image_tool, search_tool, model
    except ImportError as e:
        st.error(f"Tool loading error: {e}")
        st.info("Make sure to install: pip install ddgs")
        st.stop()
    except Exception as e:
        st.error(f"Initialization error: {e}")
        st.stop()

# Load tools and model
image_tool, search_tool, model = initialize_tools()

# Save image in memory
def display_image(b64_string):
    try:
        data = base64.b64decode(b64_string)
        st.image(data, use_column_width=True)
    except Exception as e:
        st.error(f"Error displaying image: {e}")

# Decide if query is image-related
def is_image_query(prompt: str) -> bool:
    keywords = [
        "draw", "picture", "photo", "image", "painting", "art", 
        "render", "generate", "illustration", "create", "make",
        "sketch", "design", "visual", "graphic"
    ]
    return any(keyword in prompt.lower() for keyword in keywords)

# Main UI
def main():
    st.title("🤖 Smolagents AI Assistant")
    st.markdown("---")
    
    # Sidebar with instructions
    with st.sidebar:
        st.header("📖 Instructions")
        st.markdown("""
        **Image Generation Keywords:**
        - draw, picture, image, art
        - generate, create, make
        - painting, illustration, sketch
        
        **Search Queries:**
        - Any other text will trigger web search
        
        **Examples:**
        - "Draw a cat in a garden"
        - "What is the weather today?"
        - "Generate a sunset painting"
        """)
    
    # Main input
    query = st.text_input("🔍 Enter your query:", placeholder="Ask me anything or request an image...")
    
    col1, col2 = st.columns([1, 4])
    with col1:
        run_button = st.button("🚀 Run", type="primary")
    with col2:
        if st.button("🗑️ Clear"):
            st.rerun()
    
    if run_button and query.strip():
        # Show query type detection
        if is_image_query(query):
            st.info("🎨 Detected: Image Generation Request")
            
            # Generate image
            st.subheader("🖼️ Generating Image...")
            with st.spinner("Creating your image..."):
                try:
                    image_result = image_tool(query)
                    if isinstance(image_result, dict) and "image" in image_result:
                        display_image(image_result["image"])
                        st.success("✅ Image generated successfully!")
                    else:
                        st.error("❌ Could not generate image. Unexpected result format.")
                        st.write("Result:", image_result)
                except Exception as e:
                    st.error(f"❌ Image generation failed: {e}")
            
            # Related search results
            st.subheader("🔍 Related Web Search Results")
            with st.spinner("Searching for related information..."):
                try:
                    info = search_tool(query)
                    if info:
                        st.write(info)
                    else:
                        st.warning("No search results found.")
                except Exception as e:
                    st.error(f"❌ Search failed: {e}")
        
        else:
            st.info("🔍 Detected: Information Search Request")
            
            # Web search only
            st.subheader("🌐 Searching for Information...")
            with st.spinner("Searching the web..."):
                try:
                    info = search_tool(query)
                    if info:
                        st.write(info)
                        st.success("✅ Search completed!")
                    else:
                        st.warning("No search results found.")
                except Exception as e:
                    st.error(f"❌ Search failed: {e}")
    
    elif run_button and not query.strip():
        st.warning("⚠️ Please enter a query before running.")

if __name__ == "__main__":
    main()

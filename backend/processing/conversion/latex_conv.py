import google.generativeai as genai
import PIL.Image

def image_to_latex(image_path, api_key):
    """
    Transcribes an image to LaTeX code using the Google Gemini API.

    Args:
        image_path (str): The path to the input image file.
        api_key (str): Your Google Gemini API key.

    Returns:
        str: The generated LaTeX code, or an error message if something went wrong.
    """
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')

    try:
        img = PIL.Image.open(image_path)
        
        # The prompt guides the model to output LaTeX
        prompt = """
        Transcribe the content in this image into LaTeX code. 
        If there are multiple equations or elements, provide them in a clear and organized LaTeX structure. 
        Focus on accuracy and proper LaTeX syntax for mathematical expressions.
        Return only the LaTeX code without any explanations, headers, or extra text.
        """
        response = model.generate_content([prompt, img])
        return response.text
    except Exception as e:
        return f"An error occurred: {e}"

if __name__ == "__main__":
    # Replace with your actual image path and API key
    # You can get an API key from https://ai.google.dev/
    image_file = r"C:\Users\zinnu\OneDrive\Desktop\math2.png"
    your_api_key = "" 

    if your_api_key == "":
        print("Error: enter API Key")
    elif image_file == "":
        print("Error: enter image path")
    else:
        print(f"Attempting to transcribe image: {image_file}")
        latex_output = image_to_latex(image_file, your_api_key)
        print("\n--- Generated LaTeX Code ---")
        print(latex_output)
        print("----------------------------")
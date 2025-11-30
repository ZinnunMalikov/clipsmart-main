import google.generativeai as genai
import PIL.Image

def image_to_latex(image_path, api_key):
    """convert image to LaTeX using Gemini API"""
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')

    try:
        img = PIL.Image.open(image_path)
        
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
    # replace with your image path and API key
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
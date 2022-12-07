import pandas as pd

def translate_text(target, text):
    """Translates text into the target language.

    Target must be an ISO 639-1 language code.
    See https://g.co/cloud/translate/v2/translate-reference#supported_languages
    """
    import six
    from google.cloud import translate_v2 as translate

    translate_client = translate.Client()

    if isinstance(text, six.binary_type):
        text = text.decode("utf-8")

    # Text can also be a sequence of strings, in which case this method
    # will return a sequence of results for each text.
    result = translate_client.translate(text, target_language=target)

    return [item["translatedText"] for item in result]

def main():
    cy_df = pd.read_csv("data\\Chengyu-Final.csv")
    chengyu = cy_df["Chengyu"].to_list()
    definitions = cy_df["Definition"].to_list()
    low_length = int(len(definitions)/20)
    definitions = definitions[(19*low_length)+1:]
    chengyu = chengyu[(19*low_length)+1:]
    english_definitions = translate_text("en", definitions)
    output_df = pd.DataFrame([chengyu, english_definitions], ["Chengyu", "Definitions"])
    output_df = output_df.transpose()
    output_df.to_csv("data\\en-definitions20.csv")
    
if __name__ == '__main__':
    main()
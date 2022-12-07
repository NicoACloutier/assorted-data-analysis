import pandas as pd

def translate_text(target, text):
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
    
    chengyu_list = pd.read_csv("data\\chengyu-appearances.csv")
    chengyu_list = chengyu_list["Chengyu"].to_list()
    
    missing_df = pd.read_csv("data\\en-definitions.csv")
    incomplete_list = missing_df["Chengyu"].to_list()
    definition_list = missing_df["Definition"].to_list()
    
    final = pd.read_csv('data\\Chengyu-Final.csv')
    chengyu_final = final["Chengyu"].to_list()
    definition_final = final["Definition"].to_list()
    final = dict(zip(chengyu_final, definition_final))
    
    missing_list = [item for item in chengyu_list if item not in incomplete_list]
    
    missing_definitions = [final[missing_chengyu] for missing_chengyu in missing_list]
    translated = translate_text("en", missing_definitions)
    
    incomplete_list += missing_list
    definition_list += missing_definitions
    
    output_df = pd.DataFrame([incomplete_list, definition_list], ["Chengyu", "Definition"])
    output_df = output_df.transpose()
    output_df.to_csv("data\\en-definitions.csv")
    

if __name__ == '__main__':
    main()
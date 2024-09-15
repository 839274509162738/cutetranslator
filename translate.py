from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer
import torch
import warnings

model = None
tokenizer = None

def load_model_and_tokenizer():
    global model, tokenizer
    if model is None or tokenizer is None:
        model_name = "facebook/m2m100_418M"
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=FutureWarning)
            tokenizer = M2M100Tokenizer.from_pretrained(model_name)
            model = M2M100ForConditionalGeneration.from_pretrained(model_name)
    return model, tokenizer

def translate(text, src_lang, tgt_lang):
    try:
        model, tokenizer = load_model_and_tokenizer()

        tokenizer.src_lang = src_lang
        encoded = tokenizer(text, return_tensors="pt")
        
        with torch.no_grad():
            generated_tokens = model.generate(
                **encoded,
                forced_bos_token_id=tokenizer.get_lang_id(tgt_lang)
            )
        
        return tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]
    except Exception as e:
        raise RuntimeError(f"Translation failed: {str(e)}")

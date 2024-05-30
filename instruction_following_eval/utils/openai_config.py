from openai import OpenAI
#
# def run_code(code_str):
#     try:
#         code_obj = compile(code_str, '<string>', 'exec')
#         exec(code_obj)
#         return True
#     except (SyntaxError, Exception):
#         return False

client = OpenAI(
    api_key="fk-garry",
    base_url="http://chat.cuhklpl.com/v1/"
)





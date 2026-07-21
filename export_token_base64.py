import base64
import os

token_file = "token.pickle"
output_file = "token_base64.txt"

if not os.path.exists(token_file):
    print(f"❌ '{token_file}' 파일이 존재하지 않습니다.")
else:
    with open(token_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(encoded)
    
    print(f"[SUCCESS] '{token_file}' encoding finished.")
    print(f"[INFO] Result saved to '{output_file}'.")
    print("GitHub Secret (TOKEN_PICKLE_BASE64) value:")
    print("-" * 50)
    print(encoded[:100] + "... (Total " + str(len(encoded)) + " chars)")
    print("-" * 50)

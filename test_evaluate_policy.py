import asyncio
from fastapi import UploadFile
from handlers.policy_handlers import handle_evaluate_policy_file

class DummyUploadFile:
    def __init__(self, file_path):
        self.filename = file_path
        self.file = open(file_path, "rb")
    async def read(self):
        return self.file.read()
    async def close(self):
        self.file.close()

async def main():
    # Path to your policy document (DOCX or PDF)
    file_path = "policies/Information-Security-Policy.docx"
    upload_file = DummyUploadFile(file_path)
    standards = ["ISO27001", "NIST800-53"]  # Example standards
    chunk_size = 1000
    speed = "deep"

    # Call the handler directly
    result = await handle_evaluate_policy_file(upload_file, standards, chunk_size, speed)
    
    # save the result to a file
    output_filename = "evaluation_result.json"
    with open(output_filename, "w") as f:
        f.write(result)
    print(f"Evaluation results saved to: {output_filename}")

    await upload_file.close()
    
if __name__ == "__main__":
    asyncio.run(main())


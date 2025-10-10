# Introduction

This repository serves as a sample implementation for a Spaya API client. 
You can use the code as-is or integrate parts of it in your own codebase.

## API Design Overview

The API allows users to submit retrosynthesis jobs comprised of batches of molecules in the form of SMILES and search parameters, and then follow the progress of the jobs to obtain results.

Once the jobs complete, the user can then query for the RScore values for each structure, or query the individual retrosynthesis routes discovered by Spaya.

## Usage

First and foremost, this sample implementation is provided as-is with no guarantee, always refer to the official and up-to-date API documentation provided here: https://spaya.ai/api/v2/docs/

This project can be run easily with Poetry in a few steps:

1. Make sure Python 3.10 or higher and Poetry are installed on your system
2. Create the virtual environment and install the dependencies
```bash
poetry install
````
3. Create a Spaya API Token in Spaya and save it to your environment
```bash
export SPAYA_API_TOKEN="your-token"
```
4. Set the URL of the Spaya API instance you use (Contact Iktos if you're not sure which URL to use)
```bash
export SPAYA_API_URL="https://spaya.ai/api/v2"
```
5. Prepare your list of SMILES in a file (You can look in the `samples` directory for examples)
6. Run the project
```bash
poetry run task run --file your-smiles-file.txt
```

If you previously ran a retrosynthesis and kept the `job id` you can reuse it to extract the results. You will obtain the `job id` when you submit a retrosynthesis job, or you can find it in Spaya in the `Activities` page.
```bash
poetry run task run --job 123456
```

If you do not wish to use Poetry, make sure to manually install all the dependencies listed in the `pyproject.toml` file and then run the program with either command below

```bash
python main.py --token ${SPAYA_API_TOKEN} --base-url ${SPAYA_API_URL} --file your-smiles-file.txt
python main.py --token ${SPAYA_API_TOKEN} --base-url ${SPAYA_API_URL} --job 123456 
```

## Code structure

Most of the code provided here serves as a wrapper to submit the jobs and display/store the results for this sample project. For a production-ready project you need to focus on the `src/helpers/spaya_api_client.py` which implements the logic of invoking the API and waiting for the results.

`src/helpers/submit_batch_from_file.py` and `src/helpers/check_batch_status.py` serve as interfaces to this file to send the SMILES and receive the scores. Your own implementation would rewrite these files to suit your project.

To keep the code easy to follow and focused on the core features of the API, only a minimal set of parameters and error checking/validations have been implemented. 
You are encouraged to follow good coding practices in your project and test for errors on every step of the API workflow.

## Disclaimer

This source code project is provided as an example for educational and illustrative purposes only. While efforts have been made to ensure the accuracy and reliability of the code, no guarantee is made regarding its suitability for any specific purpose.

By accessing and using this source code, you agree that:

1. The code is provided "as is" without warranty of any kind, express or implied.
2. You acknowledge that you are solely responsible for any consequences resulting from the use of this code.
3. The author(s) and contributors of this code shall not be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits; or business interruption) arising in any way out of the use of this code, even if advised of the possibility of such damage.
4. Copyright © 2024 Iktos. All rights reserved.

  
This disclaimer does not limit or exclude any liability for death or personal injury resulting from negligence, fraud, or any other liability that cannot be excluded or limited under applicable law.

Use of this source code project implies acceptance of these terms.
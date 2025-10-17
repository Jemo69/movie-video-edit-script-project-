# Configuring GitHub Secrets

To run the GitHub Action workflow for this project, you need to add the following secrets to your GitHub repository. Secrets are encrypted environment variables that are only exposed to selected actions.

## Why Use Secrets?

It is crucial **not** to commit sensitive information like API keys or passwords directly into your git repository. Storing them as GitHub Secrets keeps them secure.

## How to Add Secrets

1.  Navigate to your repository on GitHub.
2.  Go to **Settings** > **Secrets and variables** > **Actions**.
3.  Click on **New repository secret**.
4.  Enter the secret name (e.g., `YOUTUBE_API_KEY`) and its corresponding value.
5.  Click **Add secret**.

## Required Secrets

You need to add the following secrets for the workflow to run successfully:

*   `YOUTUBE_API_KEY`: Your API key for the YouTube Data API.
*   `SENDER_EMAIL`: The email address used to send notification emails.
*   `SENDER_PASSWORD`: The password for the sender's email account.
*   `GOOGLE_APPLICATION_CREDENTIALS_JSON`: The JSON content of your Google Cloud service account key file (`key.json`).

### How to get `GOOGLE_APPLICATION_CREDENTIALS_JSON`

1.  Open your `key.json` file.
2.  Copy the entire JSON content of the file.
3.  When creating the `GOOGLE_APPLICATION_CREDENTIALS_JSON` secret in GitHub, paste the copied JSON content into the value field.

**Note:** The GitHub Action workflow will take the content of this secret, write it to a temporary file, and then set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to the path of that file. This is the standard way to provide credentials to Google Cloud client libraries.

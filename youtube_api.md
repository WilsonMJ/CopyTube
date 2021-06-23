# Obtaining YouTube API Key and client_secrets JSON

1. Navigate to the [Cloud Console API Dashboard](https://console.cloud.google.com/apis/dashboard) and login with your Google account if needed.

2. Click on **ENABLE APIS AND SERVICES**

    ![Google Cloud Console Dashboard](captures/1.png)

3. In the searchbox, search for **YouTube Data API V3** and click on the result

    ![API Searchbox](captures/2.png)

4. Click **Enable**

    ![Enable YouTube Data API](captures/3.png)

5. On the page you're redirected to, click on **Credentials**

    ![Credentials first click](captures/4.png)

6. Click on **CONFIGURE CONSENT SCREEN**. 
    - Your consent screen will need to be configured in order to obtain OAuth credentials for creating a playlist and adding videos to your account.

    ![Configure Consent Screen](captures/5.png)

7. Choose **External** for User Type and click **CREATE**

    ![Consent Screen User Type](captures/6.png)

8. Fill out the required information on this form indicated by the red asterisks and click **SAVE AND CONTINUE**.

    ![Consent Screen App Info](captures/7.png)

    ![Consent Screen App Info 2](captures/8.png)

9. For the **Scopes** page and **Test users** page, just click **SAVE AND CONTINUE**.
    
    ![Scopes and Test Users Continue](captures/9.png)

    ![Scopes and Test Users Continue 2](/captures/10.png)

10. You will then arrive at the **OAuth consent screen** summary page. From here, click **Credentials**.

    ![OAuth Summary](captures/11.png)

11. On the credentials page, click **CREATE CREDENTIALS** and select **API key**.
    - You have now generated the API key you should place in the **DEVELOPER KEY** variable found in [config.py](config.py)

    ![Generate API key](/captures/12.png)

    ![API Key info](/captures/13.png)

12. Click **CREATE CREDENTIALS** again and select **OAuth client ID**.

    ![Generate OAuth 2.0](captures/14.png)

13. For **Application type**, select **Desktop** and click **CREATE**.

    ![OAuth App type](captures/15.png)

14. Click **OK** on the screen that appears and click on the Download icon next to the newly created OAuth 2.0 Client ID.  Save this file into the same directory as [copytube.py](copytube.py).
    - Add the name of this file including .json to the **CLIENT_SECRETS_FILE** variable found in [config.py](config.py)

    ![OAuth Confirmation](captures/16.png)

    ![OAuth Download](captures/17.png)

15. From the **Credentials** screen, click on **OAuth consent screen**.

    ![OAuth consent screen click](captures/23.png)

16. On the **OAuth consent screen** page under **Publishing status**, click **PUBLISH APP** and **CONFIRM**.

    ![OAuth Publish App](captures/24.png)

    ![Publish App confirm](captures/25.png)

15. You have now obtained all the necessary credentials to use CopyTube and setup the API for use with your google accounts!
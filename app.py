import streamlit as st
import os
import asyncio

from session_state import get
from httpx_oauth.clients.google import GoogleOAuth2


async def write_authorization_url(client,
                                  redirect_uri):
    authorization_url = await client.get_authorization_url(
        redirect_uri,
        scope=["email"],
        extras_params={"access_type": "offline"},
    )
    return authorization_url


async def write_access_token(client,
                             redirect_uri,
                             code):
    token = await client.get_access_token(code, redirect_uri)
    return token


def main():
    st.write("You're logged in")


if __name__ == '__main__':
    client_id = os.environ['GOOGLE_CLIENT_ID']
    client_secret = os.environ['GOOGLE_CLIENT_SECRET']
    redirect_uri = os.environ['REDIRECT_URI']

    client = GoogleOAuth2(client_id, client_secret)
    authorization_url = asyncio.run(
        write_authorization_url(client=client,
                                redirect_uri=redirect_uri)
    )

    session_state = get(token=None)
    if session_state.token is None:
        try:
            code = st.experimental_get_query_params()['code']
        except:
            st.write(f'''<h1>
                Please login using this <a target="_self"
                href="{authorization_url}">url</a></h1>''',
                     unsafe_allow_html=True)
        else:
            # Verify token is correct:
            try:
                token = asyncio.run(
                    write_access_token(client=client,
                                       redirect_uri=redirect_uri,
                                       code=code))
            except:
                st.write(f'''<h1>
                    This account is not allowed or page was refreshed.
                    Please try again: <a target="_self"
                    href="{authorization_url}">url</a></h1>''',
                         unsafe_allow_html=True)
            else:
                # Check if token has expired:
                if token.is_expired():
                    if token.is_expired():
                        st.write(f'''<h1>
                        Login session has ended,
                        please <a target="_self" href="{authorization_url}">
                        login</a> again.</h1>
                        ''')
                else:
                    session_state.token = token
                    main()
    else:
        main()

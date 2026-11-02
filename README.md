# Utility Manager

Hourly charts of electrical use (Emporia Utility Connect) and HVAC runtime (ecobee),
published to http://static.yawn.live/utilitymgr/.

Get started:

    python3 -m venv venv
    . venv/bin/activate
    pip3 install -r requirements.txt

## Credentials

`runner.py` reads OAuth refresh tokens from GCS (`gs://static.yawn.live/utilitymgr/*_token.json`)
and refreshes them on every run. Neither vendor offers API keys, so seed them once with
`bootstrap_auth.py`:

- **ecobee**: put `ECOBEE_USERNAME` / `ECOBEE_PASSWORD` in `.env` and run
  `python bootstrap_auth.py ecobee` (prompts for an MFA code if enabled). Setting the same
  env vars on the runner lets it log in again if the refresh token is revoked.
- **Emporia** (Google sign-in, so no password): log in at https://web.emporiaenergy.com,
  then in the browser console dump IndexedDB `com.amplify.awsCognitoAuthPlugin` /
  `default.store` to `emporia_store.json` and run `python bootstrap_auth.py emporia`.
  Repeat if the refresh token expires (the run will fail with "Emporia token refresh failed").

```javascript
(async () => {
  const db = await new Promise((ok, no) => { const r = indexedDB.open('com.amplify.awsCognitoAuthPlugin'); r.onsuccess = () => ok(r.result); r.onerror = no; });
  const st = db.transaction('default.store').objectStore('default.store');
  const get = r => new Promise(ok => r.onsuccess = () => ok(r.result));
  const [keys, vals] = await Promise.all([get(st.getAllKeys()), get(st.getAll())]);
  const out = Object.fromEntries(keys.map((k, i) => [k, vals[i]]));
  window.__emporia = JSON.stringify(out, null, 2);
  console.table(keys.map((k, i) => ({ key: k, length: JSON.stringify(vals[i]).length })));
})();
// then, as a separate console command once the table prints:
copy(window.__emporia)
```

Then upload the token files with the `gsutil cp` commands in `bootstrap_auth.py`.

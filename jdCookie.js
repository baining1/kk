const fs = require('fs');
let CookieJDs = [];
const defaultFileName = 'jdCookie.txt';

function loadCookieFromEnv(envName) {
  let cookies = [];
  if (envName && envName.length > 90) {
    if (envName.indexOf('&') > -1) {
      cookies = envName.split('&');
    } else if (envName.indexOf('\n') > -1) {
      cookies = envName.split('\n');
    } else {
      cookies = [envName];
    }
  }
  cookies = [...new Set(cookies.filter((item) => !!item))];
  return cookies;
}

function loadCookieFromFile(fileName) {
  let cookies = [];
  if (fs.existsSync(fileName)) {
    const ckText = fs.readFileSync(fileName);
    const list = ckText
      .toString()
      .split('\n')
      .filter(
        (item) => item.indexOf('pt_pin') >= 0 && item.indexOf('pt_key') >= 0
      );
    cookies = list.map((tempCk) => {
      const pt_pin = tempCk.match(/pt_pin=.+?;/)[0];
      const pt_key = tempCk.match(/pt_key=.+?;/)[0];
      const ck = pt_key + pt_pin;
      return ck;
    });
  }
  cookies = [...new Set(cookies.filter((item) => !!item))];
  return cookies;
}

function endOfLoad(cookies) {
  console.log(`[jdCookie] 共${cookies.length}个京东账号Cookie\n`);
  module.exports = cookies;
}
function main() {
  console.log(
    `\n[jdCookie] 脚本执行 - 北京时间(UTC+8)：${new Date(
      new Date().getTime() +
        new Date().getTimezoneOffset() * 60 * 1000 +
        8 * 60 * 60 * 1000
    ).toLocaleString()}`
  );

  // 然后读取本地文件
  CookieJDs = loadCookieFromFile(defaultFileName);
  if (CookieJDs.length > 0) {
    console.log(`[jdCookie] Cookie来自 defaultFileName: ${defaultFileName}`);
    return endOfLoad(CookieJDs);
  }
}
main();

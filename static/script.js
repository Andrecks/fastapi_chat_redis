function getNicknameFromCookie() {
    const cookies = document.cookie.split(";")
      .map(cookie => cookie.trim())
      .reduce((acc, cookie) => {
        const [name, value] = cookie.split("=");
        return { ...acc, [name]: decodeURIComponent(value) };
      }, {});
  
    return cookies.hasOwnProperty("nickname") ? cookies["nickname"] : null;
  }
  
  const nickname = getNicknameFromCookie();
  if (nickname) {
    // Cookie exists, perform some action with the nickname value
    console.log("Nickname:", nickname);
  } else {
    // Cookie does not exist, perform some other action
    console.log("Nickname cookie does not exist");
  }
document.addEventListener("DOMContentLoaded", function () {
  if (
    (!localStorage.getItem("cookiesAccepted") ||
      localStorage.getItem("cookiesAccepted") === "false") &&
    !sessionStorage.getItem("cookiePopupShown")
  ) {
    setTimeout(function () {
      document.getElementById("cookieConsent").style.display = "block";
      sessionStorage.setItem("cookiePopupShown", "true");
    }, 15000);
  }

  document
    .getElementById("acceptCookies")
    .addEventListener("click", function () {
      localStorage.setItem("cookiesAccepted", "true");
      document.getElementById("cookieConsent").style.display = "none";
    });

  document.getElementById("denyCookies").addEventListener("click", function () {
    localStorage.setItem("cookiesAccepted", "false");
    document.getElementById("cookieConsent").style.display = "none";
  });

  document
    .getElementById("closeCookieBox")
    .addEventListener("click", function () {
      document.getElementById("cookieConsent").style.display = "none";
    });
});

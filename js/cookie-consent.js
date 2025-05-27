document.addEventListener("DOMContentLoaded", function () {
  // Show popup only if:
  // - No acceptance stored
  // - OR user previously denied
  // AND popup hasn't already shown in this session
  if (
    (!localStorage.getItem("cookiesAccepted") ||
      localStorage.getItem("cookiesAccepted") === "false") &&
    !sessionStorage.getItem("cookiePopupShown")
  ) {
    setTimeout(function () {
      document.getElementById("cookieConsent").style.display = "block";
      sessionStorage.setItem("cookiePopupShown", "true"); // show only once per session
    }, 15000); // 15 seconds
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
    // Popup will reappear next session
  });

  document
    .getElementById("closeCookieBox")
    .addEventListener("click", function () {
      document.getElementById("cookieConsent").style.display = "none";
      // No decision stored, so may reappear next session
    });
});

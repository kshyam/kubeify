document.addEventListener("DOMContentLoaded", function () {
  // Check if enough time has passed (e.g., 5 hours)
  var lastShown = localStorage.getItem("delayedModalTimestamp");
  var fiveHoursInMs = 5 * 60 * 60 * 1000;

  if (!lastShown || Date.now() - parseInt(lastShown) > fiveHoursInMs) {
    // Show the modal after 5 seconds
    setTimeout(function () {
      var modalElement = document.getElementById("delayedModal");
      if (modalElement) {
        var bootstrapModal = new bootstrap.Modal(modalElement);
        bootstrapModal.show();
      }
      // Store the current timestamp in localStorage after showing it
      localStorage.setItem("delayedModalTimestamp", Date.now());
    }, 5000);
  }
});

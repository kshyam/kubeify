document.addEventListener("DOMContentLoaded", function () {
  if (!sessionStorage.getItem("delayedModalShown")) {
    // Mark as shown immediately to prevent race conditions
    sessionStorage.setItem("delayedModalShown", "true");

    setTimeout(function () {
      var modalElement = document.getElementById("delayedModal");
      if (modalElement) {
        // For Bootstrap 5:
        var bootstrapModal = new bootstrap.Modal(modalElement);
        bootstrapModal.show();
      }
    }, 5000); // Show after 5 seconds
  }
});

document.addEventListener("DOMContentLoaded", function () {
  if (!localStorage.getItem("delayedModalShown")) {
    // Mark as shown immediately to prevent race conditions
    localStorage.setItem("delayedModalShown", "true");

    setTimeout(function () {
      var modalElement = document.getElementById("delayedModal");
      if (modalElement) {
        var bootstrapModal = new bootstrap.Modal(modalElement);
        bootstrapModal.show();
      }
    }, 5000); // Show after 5 seconds
  }
});

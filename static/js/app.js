// Show loading spinner on generate form submit
(function () {
  const form = document.getElementById("generateForm");
  if (form) {
    form.addEventListener("submit", function () {
      const btnText = document.getElementById("btnText");
      const btnSpinner = document.getElementById("btnSpinner");
      if (btnText) btnText.classList.add("d-none");
      if (btnSpinner) btnSpinner.classList.remove("d-none");
      form.classList.add("loading");
    });
  }
})();

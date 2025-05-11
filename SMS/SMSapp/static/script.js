// For sidebar toggle feature
document.addEventListener("DOMContentLoaded", function () {
    const toggler = document.querySelector(".toggler-btn");

    if (toggler) {
        toggler.addEventListener("click", function(){
            document.querySelector("#sidebar").classList.toggle("collapsed");
        });
    }
});
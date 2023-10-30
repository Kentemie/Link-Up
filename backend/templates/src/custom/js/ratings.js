const ratingButtons = document.querySelectorAll('.rating-buttons');
console.log("Some gibberish")
ratingButtons.forEach(button => {
    button.addEventListener('click', event => {

        // Getting the rating value from the data attribute of the button
        const value = parseInt(event.target.dataset.value)
        const articleId = parseInt(event.target.dataset.article)
        const ratingSum = button.querySelector('.rating-sum');

        // Create a FormData object to send data to the server
        const formData = new FormData();

        // Add article id, button value
        formData.append('article_id', articleId);
        formData.append('value', value);

        // Sending an AJAX Request to the server
        fetch("/rating/", {
            method: "POST",
            headers: {
                "X-CSRFToken": csrftoken,
                "X-Requested-With": "XMLHttpRequest",
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => {

            // Update the value on the button
            ratingSum.textContent = data.rating_sum;
        })
        .catch(error => console.error(error));
    });
});

// This code sets up a click handler for the rating buttons, which have the class 'rating-buttons'. When the user clicks 
// on one of the buttons, the rating value is extracted from the data attribute of the button, as well as the id of the article 
// that the user rated. A FormData object is then created that contains this information and an AJAX request is sent to the server 
// using the fetch() method. The request header contains a CSRF token and an X-Requested-With header with the value XMLHttpRequest.
// After receiving the server response, the total rating value is updated on the button using the textContent method.
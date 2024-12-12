function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

const question_cards = document.getElementsByClassName("question-card");
const answer_cards = document.getElementsByClassName("answer-card");

console.log(answer_cards);

for (const card of question_cards) {
  const likeButton = card.querySelector(".like-button");
  const dislikeButton = card.querySelector(".dislike-button");
  const likeCounter = card.querySelector(".like-counter");
  const questionId = card.dataset.item;

  likeButton.addEventListener("click", () => {
    const request = new Request(`/like/question/${questionId}/`, {
      method: "POST",
      headers: { "X-CSRFToken": getCookie("csrftoken") },
      mode: "same-origin",
      body: JSON.stringify({ type: 1 }),
    });

    fetch(request).then((response) => {
      response.json().then((data) => {
        likeCounter.value = data.likes_count;
      });
    });
  });

  dislikeButton.addEventListener("click", () => {
    const request = new Request(`/like/question/${questionId}/`, {
      method: "POST",
      headers: { "X-CSRFToken": getCookie("csrftoken") },
      mode: "same-origin",
      body: JSON.stringify({ type: -1 }),
    });

    fetch(request).then((response) => {
      response.json().then((data) => {
        likeCounter.value = data.likes_count;
      });
    });
  });
}

for (const card of answer_cards) {
  const likeButton = card.querySelector(".like-button");
  const dislikeButton = card.querySelector(".dislike-button");
  const likeCounter = card.querySelector(".like-counter");
  const correctCheckBox = card.querySelector(".correct-answer");
  const answerId = card.dataset.item;

  likeButton.addEventListener("click", () => {
    const request = new Request(`/like/answer/${answerId}/`, {
      method: "POST",
      headers: { "X-CSRFToken": getCookie("csrftoken") },
      mode: "same-origin",
      body: JSON.stringify({ type: 1 }),
    });

    fetch(request).then((response) => {
      response.json().then((data) => {
        likeCounter.value = data.likes_count;
      });
    });
  });

  dislikeButton.addEventListener("click", () => {
    const request = new Request(`/like/answer/${answerId}/`, {
      method: "POST",
      headers: { "X-CSRFToken": getCookie("csrftoken") },
      mode: "same-origin",
      body: JSON.stringify({ type: -1 }),
    });

    fetch(request).then((response) => {
      response.json().then((data) => {
        likeCounter.value = data.likes_count;
      });
    });
  });

    if (correctCheckBox) {
        correctCheckBox.addEventListener("click", () => {
            const request = new Request(`/correct/answer/${answerId}/`, {
            method: "POST",
            headers: { "X-CSRFToken": getCookie("csrftoken") },
            mode: "same-origin",
            });

            fetch(request).then((response) => {
            response.json().then((data) => {
                correctCheckBox.checked = data.is_correct;

                if (data.is_correct) {
                card.classList.add("border-success", "border-2");
                } else {
                card.classList.remove("border-success", "border-2");
                }
            });
            });
        });
    } 
}

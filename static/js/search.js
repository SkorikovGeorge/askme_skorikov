const searchInput = document.getElementById('search-input');
const resultsDropdown = document.getElementById("search-results");

searchInput.addEventListener('keyup', function() {
  clearTimeout(this.timer);

  if (this.value.length < 3) {
    resultsDropdown.innerHTML = '';
    resultsDropdown.classList.remove('show');
    return;
  }

  this.timer = setTimeout(() => {
    fetch('/search/?q=' + this.value, { 
      headers: { 'X-CSRFToken': getCookie('csrftoken') }
    })
    .then(response => response.json())
    .then(data => {
      resultsDropdown.innerHTML = '';
      resultsDropdown.classList.remove('show');

      if (data.results.length > 0) {
        data.results.forEach(result => {
          resultsDropdown.innerHTML += `<li><a class="dropdown-item" href="${result.url}">${result.title}</a></li>`;
        });
        resultsDropdown.classList.add('show');
      } 
      else {
        resultsDropdown.innerHTML = '<li class="dropdown-item disabled">No results</li>';  
        resultsDropdown.classList.add('show');
      }
    });
  }, 500);
});


document.addEventListener('click', function(e) {
  const isClickInsideDropdown = resultsDropdown.contains(e.target) || (e.target.closest('.dropdown-menu') && e.target.closest('.dropdown-menu')!== resultsDropdown);
  if (!searchInput.contains(e.target) && !isClickInsideDropdown ) {
    resultsDropdown.classList.remove('show');
  }
});

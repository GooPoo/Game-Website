// Get the CSRF token from the hidden input
const csrfToken = document.getElementById('csrf_token').value;

// FOR DEVELOPMENT ONLY, DELETE THIS SECTION FOR PRODUCTION
document.getElementById('delete-game').addEventListener('click', function() {
  if (confirm("Are you sure you want to delete this game? This action cannot be undone.")) {
      console.log('Deleting game with ID:', gameId);
      fetch('/delete_game', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': csrfToken,
          },
          body: JSON.stringify({ game_id: gameId })
      })
      .then(response => response.json())
      .then(data => {
          if (data.error) {
              alert(data.error);
          } else {
              alert(data.message);
              window.location.href = '/';
          }
      })
      .catch(error => console.error('Error:', error));
  }
});
//=================================================================================

document.addEventListener("DOMContentLoaded", () => {
    createSquares();
    getGuesses();
  
    let guessedWords = [[]];
    let availableSpace = 1;
  
    let guessedWordCount = 0;
    let gameOver = false;
  
    const keys = document.querySelectorAll(".keyboard-row button");
    const overlayContainer = document.querySelector(".overlay-container");
    const overlayHeaderMessage = document.querySelector(".overlay-headerMessage");
    const overlayMessage = document.querySelector(".overlay-message");
    const overlayAttempts= document.querySelector(".overlay-attempts");
    const overlayScore = document.querySelector(".overlay-score");
    const overlayPosition = document.querySelector(".overlay-postition");
    const overlayDataContainer = document.querySelector(".overlay-dataContainer");

    let overlaybtn = document.querySelector('#overlay-btn')

    overlaybtn.onclick = function () {
      overlayContainer.style.display = "none";
    }

    function getGuesses() {
      fetch(`/get_guesses/${gameId}`)
          .then(response => {
              if (!response.ok) {
                  throw new Error('Network response was not ok');
              }
              return response.json();
          })
          .then(guesses => {
              if (guesses.length === 0) {
                  console.log('No guesses found.');
                  return;
              }
  
              // Iterate over the previous guesses and render them on the board
              guesses.forEach((guess, guessIndex) => {
                  const wordArr = guess.guess_word.split("");
                  wordArr.forEach((letter, letterIndex) => {
                      const tileId = guessIndex * 5 + letterIndex + 1;
                      const tile = document.getElementById(tileId);
                      tile.textContent = letter;
                      const tileColor = getTileColor(parseInt(guess.guess_score[letterIndex]));
                      tile.style = `background-color:${tileColor};border-color:${tileColor}`;
                      tile.classList.add("animate__flipInX");

                      // Update the keyboard key color
                      updateKeyboard(letter, parseInt(guess.guess_score[letterIndex]));
                  });
  
                  guessedWords[guessIndex] = wordArr; // Update guessedWords with the fetched guess

                  if (guess.guess_score === '22222') {
                    gameOver = true;
                    displayOverlay("You've won the game. Come back tomorrow for more games.");
                  }
              });
              if (guesses.length === 6 && gameOver !== true) {
                gameOver = true;
                displayOverlay("Sorry, you have no more guesses! Try again tomorrow.", true);
              }
              // Update guessedWordCount and availableSpace
              guessedWordCount = guesses.length;
              availableSpace = guessedWordCount * 5 + 1; // Set availableSpace to the next empty square
              guessedWords.push([]); // Prepare the next array for the current word being guessed

              // If the game is over, disable further input
              if (gameOver) {
                disableInput();
            }
          })
          .catch(error => {
              console.error('Error fetching guesses:', error);
          });
  }
  
    function getCurrentWordArr() {
      const numberOfGuessedWords = guessedWords.length;
      return guessedWords[numberOfGuessedWords - 1];
    }
  
    function updateGuessedWords(letter) {
      if (gameOver) return;

      const currentWordArr = getCurrentWordArr();
  
      if (currentWordArr && currentWordArr.length < 5) {
        currentWordArr.push(letter);
  
        const availableSpaceEl = document.getElementById(String(availableSpace));
  
        availableSpace = availableSpace + 1;
        availableSpaceEl.textContent = letter;
      }
    }
  
    function getTileColor(feedback) {
      // The feedback is a number: 0 (not in word), 1 (in word but wrong position), 2 (correct position)
      if (feedback === 2) {
        return "rgb(83, 141, 78)"; //green
      } else if (feedback === 1) { 
        return "rgb(181, 159, 59)"; //yellow
      } else {
        return "rgb(58, 58, 60)"; // dark grey
      }
    }

    function updateKeyboard(letter, feedback) {
        const key = document.querySelector(`[data-key="${letter}"]`);
        if (!key) return; // Prevent errors if the key isn't found
    
        const tileColor = getTileColor(feedback);
    
        // Define color priorities
        const colorPriority = {
            "rgb(58, 58, 60)": 0, // dark grey (not in word)
            "rgb(181, 159, 59)": 1, // yellow (in word but wrong position)
            "rgb(83, 141, 78)": 2 // green (correct position)
        };
    
        // Get the current color of the key
        const currentColor = key.style.backgroundColor;
    
        // Only update if the new color has a higher priority
        if (!currentColor || colorPriority[tileColor] > colorPriority[currentColor]) {
            key.style.backgroundColor = tileColor;
            key.style.borderColor = tileColor;
        }
    }
  
  
  
  
    function handleSubmitWord() {
      if (gameOver) return;

      const currentWordArr = getCurrentWordArr();
      if (currentWordArr.length !== 5) {
        console.log("Word must be 5 letters");
        return;
      }
    
      const currentWord = currentWordArr.join("");
    
      fetch(`/submitWordleWord`, {
        method: "POST",
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
        },
        body: JSON.stringify({ word: currentWord, game_id: gameId })
    
      })
      .then(async (res) => {
        const data = await res.json();
        if (!res.ok) {
          console.log(data.error || 'Network response was not ok'); // Visual cue Needed.
          return;
        }
        
        // The response should be a string of 5 integers
        const feedback = data.feedback.trim().split("").map(Number).filter(num => !isNaN(num));
        console.log(feedback);
    
        const firstLetterId = guessedWordCount * 5 + 1;
        const interval = 200;
        currentWordArr.forEach((letter, index) => {
          setTimeout(() => {
            if (index >= feedback.length) {
              console.error("Index out of bounds for feedback array");
              return;
            }
    
            const tileColor = getTileColor(feedback[index]);
    
            const letterId = firstLetterId + index;
            const letterEl = document.getElementById(letterId);
            letterEl.classList.add("animate__flipInX");
            letterEl.style = `background-color:${tileColor};border-color:${tileColor}`;

            // Update the keyboard key color
            updateKeyboard(letter, feedback[index]);
          }, interval * index);
        });
    
        guessedWordCount += 1;
        
        // Check if the feedback indicates a win (all correct)
        if (feedback.join('') === '22222') {
          gameOver = true;
          displayOverlay("You've won the game. Come back tomorrow for more games.");
        }
    
        if (guessedWords.length === 6 && feedback.join('') !== '22222') {
          gameOver = true;
          displayOverlay("Sorry, you have no more guesses! Try again tomorrow.", true);
        }
    
        guessedWords.push([]);
      })
      .catch((error) => {
        // Usually Invalid word
        console.log(error.message); // Log or replace with a visual cue
      });
    }
    
  
  
    function createSquares() {
      const gameBoard = document.getElementById("board");
  
      for (let index = 0; index < 30; index++) {
        let square = document.createElement("div");
        square.classList.add("square");
        square.classList.add("animate__animated");
        square.setAttribute("id", index + 1);
        gameBoard.appendChild(square);
      }
    }
  
    function handleDeleteLetter() {
      if (gameOver) return;

      const currentWordArr = getCurrentWordArr();

      // Prevent deletion if there are no letters in the current word
      if (currentWordArr.length === 0) {
        return;
      }

      const removedLetter = currentWordArr.pop();
  
      guessedWords[guessedWords.length - 1] = currentWordArr;
  
      const lastLetterEl = document.getElementById(String(availableSpace - 1));
  
      lastLetterEl.textContent = "";
      availableSpace = availableSpace - 1;
    }

    function displayOverlay(message, isGameLost = false) {

      if (!overlayMessage || !overlayContainer || !overlayHeaderMessage || !overlayAttempts || !overlayScore || !overlayPosition) {
          return;
      }
      fetch(`/get_overlay_data/${gameId}`)
        .then(response => response.json())
        .then(data => {
          if (isGameLost) {
            overlayHeaderMessage.textContent = 'Unlucky ' + user + '!'
          }
          else {
            overlayHeaderMessage.textContent = 'Congratulations ' + user + '!'
          }
          overlayMessage.textContent = message;
          overlayAttempts.textContent = `Attempts: ${data.num_attempts}`;
          overlayScore.textContent = `Score: ${data.score}`;
          overlayPosition.textContent = `Current Rank: ${data.position}`;

          overlayContainer.style.display = "flex";
          overlayDataContainer.style.display = "flex";

          setTimeout(() => {
            overlayContainer.style.visibility = "visible";
            overlayContainer.style.opacity = 1;
            overlayDataContainer.style.visibility = "visible";
            overlayDataContainer.style.opacity = 1;
          }, 1000);
        })
        .catch(error => {
            console.error('Error fetching overlay data:', error);
        });
    }

    function disableInput() {
        keys.forEach(key => {
            key.onclick = null; // Remove the click event listener
        });
    }
  
    for (let i = 0; i < keys.length; i++) {
      keys[i].onclick = ({ target }) => {
        const letter = target.getAttribute("data-key");
  
        if (letter === "enter") {
          handleSubmitWord();
          return;
        }
  
        if (letter === "del") {
          handleDeleteLetter();
          return;
        }
  
        updateGuessedWords(letter);
      };
    }
  });
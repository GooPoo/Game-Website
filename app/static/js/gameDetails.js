document.addEventListener("DOMContentLoaded", () => {
    createSquares();
    getGuesses();

    let guessedWords = [[]];
    let availableSpace = 1;

    let guessedWordCount = 0;    

    function getGuesses() {
    fetch(`/words/getGuesses/${gameId}`)
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
                });

                guessedWords[guessIndex] = wordArr; // Update guessedWords with the fetched guess

            });

            // Update guessedWordCount and availableSpace
            guessedWordCount = guesses.length;
            availableSpace = guessedWordCount * 5 + 1; // Set availableSpace to the next empty square
            guessedWords.push([]); // Prepare the next array for the current word being guessed

        })
        .catch(error => {
            console.error('Error fetching guesses:', error);
        });
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
});
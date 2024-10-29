let calendar = document.querySelector('.calendar')

const month_names = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

isLeapYear = (year) => {
    return (year % 4 === 0 && year % 100 !== 0 && year % 400 !== 0) || (year % 100 === 0 && year % 400 ===0)
}

getFebDays = (year) => {
    return isLeapYear(year) ? 29 : 28
}

// Function to parse the formattedDate
const parseFormattedDate = (formattedDate) => {
    const dateParts = formattedDate.split(" ");
    const day = parseInt(dateParts[0], 10);
    const month = month_names.indexOf(dateParts[1]);
    const year = parseInt(dateParts[2], 10);
    return { day, month, year };
}

// Initialize selected date variables
let selectedDay, selectedMonth, selectedYear;

generateCalendar = (month, year) => {
    let calendar_days = calendar.querySelector('.calendar-days');
    let calendar_header_year = calendar.querySelector('#year');

    let days_of_month = [31, getFebDays(year), 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];

    calendar_days.innerHTML = '';

    let currDate = new Date();
    if (month == null) month = currDate.getMonth();
    if (!year) year = currDate.getFullYear();

    // Use parsed date to highlight and select the current date
    let parsedDate = parseFormattedDate(formattedDate);
    selectedDay = selectedDay ?? parsedDate.day;
    selectedMonth = selectedMonth ?? parsedDate.month;
    selectedYear = selectedYear ?? parsedDate.year;

    let curr_month = `${month_names[month]}`;
    month_picker.innerHTML = curr_month;
    calendar_header_year.innerHTML = year;

    let first_day = new Date(year, month, 1);

    for (let i = 0; i <= days_of_month[month] + first_day.getDay() - 1; i++) {
        let day = document.createElement('div');
        if (i >= first_day.getDay()) {
            day.classList.add('calendar-day-hover');
            day.innerHTML = i - first_day.getDay() + 1;
            day.innerHTML += `<span></span><span></span><span></span><span></span>`;
            
            // Highlight the current date based on formattedDate
            if (i - first_day.getDay() + 1 === selectedDay && year === selectedYear && month === selectedMonth) {
                day.classList.add('curr-date');
            }

            // Add click event to select a new date
            day.onclick = () => {
                selectedDay = i - first_day.getDay() + 1;
                selectedMonth = month;
                selectedYear = year;
                generateCalendar(selectedMonth, selectedYear);  // Re-render calendar with the new selected date
            };
        }
        calendar_days.appendChild(day);
    }
}

// Add event listener to the "Generate" button
document.querySelector('.continue').onclick = () => {
    // Format the selected date for the leaderboard route
    const newDate = `${selectedYear}-${(selectedMonth + 1).toString().padStart(2, '0')}-${selectedDay.toString().padStart(2, '0')}`;
    window.location.href = `/words/leaderboard/${newDate}`;
};

let month_list = calendar.querySelector('.month-list')

month_names.forEach((e, index) => {
    let month = document.createElement('div')
    month.innerHTML = `<div data-month="${index}">${e}</div>`
    month.querySelector('div').onclick = () => {
        month_list.classList.remove('show')
        curr_month.value = index
        generateCalendar(index, curr_year.value)
    }
    month_list.appendChild(month)
})

let month_picker = calendar.querySelector('#month-picker')

month_picker.onclick = () => {
    month_list.classList.add('show')
}

let currDate = parseFormattedDate(formattedDate);

let curr_month = {value: currDate.month};
let curr_year = {value: currDate.year};

generateCalendar(curr_month.value, curr_year.value)

document.querySelector('#prev-year').onclick = () => {
    --curr_year.value
    generateCalendar(curr_month.value, curr_year.value)
}

document.querySelector('#next-year').onclick = () => {
    ++curr_year.value
    generateCalendar(curr_month.value, curr_year.value)
}
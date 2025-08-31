document.addEventListener('DOMContentLoaded', () => {
    const studentForm = document.getElementById('student-form');
    const studentIdInput = document.getElementById('student-id');
    const nameInput = document.getElementById('name');
    const ageInput = document.getElementById('age');
    const gradeInput = document.getElementById('grade');
    const studentTableBody = document.querySelector('#student-table tbody');

    let students = JSON.parse(localStorage.getItem('students')) || [];

    const renderStudents = () => {
        studentTableBody.innerHTML = '';
        students.forEach((student, index) => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${student.name}</td>
                <td>${student.age}</td>
                <td>${student.grade}</td>
                <td>
                    <button class="edit-btn" data-index="${index}">Edit</button>
                    <button class="delete-btn" data-index="${index}">Delete</button>
                </td>
            `;
            studentTableBody.appendChild(tr);
        });
    };

    const saveStudents = () => {
        localStorage.setItem('students', JSON.stringify(students));
    };

    studentForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const studentId = studentIdInput.value;
        const name = nameInput.value;
        const age = ageInput.value;
        const grade = gradeInput.value;

        if (studentId) {
            // Update existing student
            students[studentId] = { name, age, grade };
        } else {
            // Add new student
            students.push({ name, age, grade });
        }

        saveStudents();
        renderStudents();
        studentForm.reset();
        studentIdInput.value = '';
    });

    studentTableBody.addEventListener('click', (e) => {
        if (e.target.classList.contains('edit-btn')) {
            const index = e.target.dataset.index;
            const student = students[index];
            studentIdInput.value = index;
            nameInput.value = student.name;
            ageInput.value = student.age;
            gradeInput.value = student.grade;
        }

        if (e.target.classList.contains('delete-btn')) {
            const index = e.target.dataset.index;
            students.splice(index, 1);
            saveStudents();
            renderStudents();
        }
    });

    renderStudents();
});

import streamlit as st

def page_one():
    left, right = st.columns([1, 2])

    with left:
        st.markdown("###### Cadence")
        st.markdown("## Let's get started")

        st.write("1️⃣ Get to know you")
        st.write("2️⃣ Your weekly routine")
        st.write("3️⃣ Your subjects")

    with right:
        st.header("Let's build a study system that works for you.")
        st.write("Hi, before we begin, I'd love to learn a bit about you...")

        # Student Type
        col1, col2 = st.columns(2)

        with col1:
            if st.button("School Student", use_container_width=True):
                st.session_state.onboarding["student_type"] = "School Student"

            if st.button("Competitive Exams", use_container_width=True):
                st.session_state.onboarding["student_type"] = "Competitive Exams"

        with col2:
            if st.button("College Student", use_container_width=True):
                st.session_state.onboarding["student_type"] = "College Student"

            if st.button("Something Else", use_container_width=True):
                st.session_state.onboarding["student_type"] = "Something Else"

        st.write(
            "Selected:",
            st.session_state.onboarding["student_type"]
        )

        st.write("What would you like help with most?")

        # Goals
        col1, col2 = st.columns(2)

        with col1:
            if st.button("Staying on top of my tasks", use_container_width=True):
                st.session_state.onboarding["goal"] = "Staying on top of my tasks"

            if st.button("Building consistent habits", use_container_width=True):
                st.session_state.onboarding["goal"] = "Building consistent habits"

            if st.button("Preparing for exams", use_container_width=True):
                st.session_state.onboarding["goal"] = "Preparing for exams"

        with col2:
            if st.button("Managing my time better", use_container_width=True):
                st.session_state.onboarding["goal"] = "Managing my time better"

            if st.button("Reducing procrastination", use_container_width=True):
                st.session_state.onboarding["goal"] = "Reducing procrastination"

            if st.button("Feeling less overwhelmed", use_container_width=True):
                st.session_state.onboarding["goal"] = "Feeling less overwhelmed"

        st.write(
            "Selected:",
            st.session_state.onboarding["goal"]
        )

        if (
            st.session_state.onboarding["student_type"] is not None
            and
            st.session_state.onboarding["goal"] is not None
        ):
            if st.button("Continue"):
                st.session_state.page = 2
                st.rerun()
        else:
            st.button("Continue", disabled=True)

def page_two():
    
    left, right = st.columns([1, 2])
    
    with right:
        st.header("Let's understand your typical week.")

        st.write("This helps us create a realistic study plan that fits around your life. No schedules, just rough amounts.")

        st.subheader("Sleep")

        sleep = st.slider(
            "How many hours do you usually sleep per night?",
            min_value=4,
            max_value=12,
            value=st.session_state.onboarding["routine"]["sleep_hours"]
        )

        school_hours = st.number_input(
            "Hours at school on a typical day?",
            min_value=0,
            max_value=12,
            value=st.session_state.onboarding["routine"]["school_hours"],
            step=1
        )

        choice = st.radio(
            "How many days per week do you attend?",
            ["5 days", "6 days", "7 days", "Custom"],
            horizontal=True
        )

        if choice == "5 days":
            school_days = 5

        elif choice == "6 days":
            school_days = 6

        elif choice == "7 days":
            school_days = 7

        else:
            school_days = st.number_input(
                "Enter number of days",
                min_value=1,
                max_value=7,
                value=5
        )
            
        st.subheader("What else regularly takes up your time?")

        routine = st.session_state.onboarding["routine"]
        col1, col2 = st.columns(2)

        with col1:
            routine["gym"] = st.checkbox(
                "Gym",
                value=routine["gym"]
            )
            routine["sports"] = st.checkbox(
                "Sports Practice",
                value=routine["sports"]
            )
            routine["family"] = st.checkbox(
                "Family Responsibilities",
                value=routine["family"]
            )
            routine["extracurricular"] = st.checkbox(
                "Extracurriculars",
                value=routine["extracurricular"]
            )

        with col2:
            routine["coaching"] = st.checkbox(
                "Coaching Classes",
                value=routine["coaching"]
            )
            routine["commute"] = st.checkbox(
                "Commute",
                value=routine["commute"]
            )
            routine["part_time"] = st.checkbox(
                "Part-Time Job",
                value=routine["part_time"]
            )

            if st.button("continue"):
                st.session_state.page = 3
                st.rerun()

        st.session_state.onboarding["routine"]["school_days"] = school_days

        st.session_state.onboarding["routine"]["sleep_hours"] = sleep

        st.session_state.onboarding["routine"]["school_hours"] = school_hours

        routine = st.session_state.onboarding["routine"]

        if st.button("Back"):
                st.session_state.page = 1
                st.rerun()

    with left:
        st.markdown("###### Cadence")

        st.write("✅ Get to know you")
        st.write("2️⃣ Weekly Routine")
        st.write("3️⃣ Subjects")

        st.divider()

        routine = st.session_state.onboarding["routine"]

        sleep = routine["sleep_hours"] * 7
        school = routine["school_hours"] * routine["school_days"]

        commitments = 0

        if routine["gym"]:
            commitments += 5

        if routine["sports"]:
            commitments += 5

        if routine["coaching"]:
            commitments += 8

        if routine["commute"]:
            commitments += 7

        if routine["part_time"]:
            commitments += 20

        if routine["family"]:
            commitments += 5

        if routine["extracurricular"]:
            commitments += 5

        free = 168 - sleep - school - commitments

        st.metric("Free hours/week", free)

        st.progress(sleep / 168)
        st.write(f"Sleep: {sleep}h")

        st.progress(school / 168)
        st.write(f"School: {school}h")

        st.progress(commitments / 168)
        st.write(f"Commitments: {commitments}h")

        st.progress(free / 168)
        st.write(f"Free for study: {free}h")

    
def page_three():
    left, right = st.columns([1, 2])

    with left:
        st.markdown("###### Cadence")

        st.write("✅ Get to know you")
        st.write("✅ Weekly Routine")
        st.write("3️⃣ Subjects")

    with right:
        st.header("Let's prepare your workspace")

        # Selected subjects

        st.subheader("Your subjects")

        selected = st.session_state.onboarding["subjects"]

        if not selected:
            st.info("No subjects selected yet.")
        else:
            for subject in selected:
                col1, col2 = st.columns([8, 1])

                with col1:
                    st.success(subject)

                with col2:
                    if st.button("❌", key=f"remove_{subject}"):
                        selected.remove(subject)
                        st.rerun()

        # Custom subject

        subject = st.text_input("Add your own subject")

        if st.button("Add Subject"):
            subject = subject.strip()

            if subject and subject not in selected:
                selected.append(subject)
                st.rerun()

        # Suggested subjects

        st.subheader("Suggested Subjects")

        suggested_subjects = [
            "Mathematics",
            "Physics",
            "Chemistry",
            "English",
            "Biology",
            "History",
            "Geography",
            "Computer Science",
            "Economics"
        ]

        cols = st.columns(3)

        visible = 0

        for subject in suggested_subjects:

            if subject not in selected:

                with cols[visible % 3]:

                    if st.button(
                        f"+ {subject}",
                        key=f"add_{subject}",
                        use_container_width=True
                    ):
                        selected.append(subject)
                        st.rerun()

                visible += 1

        #st.write(st.session_state.onboarding)
        col1, col2 = st.columns(2)

        with col1:
            if st.button("⬅ Back", use_container_width=True):
                st.session_state.page = 2
                st.rerun()

        with col2:
            if len(st.session_state.onboarding["subjects"]) >= 2:
                if st.button("Finish Setup", use_container_width=True):
                    st.session_state.page = 4
                    st.rerun()
            else:
                st.button("Finish Setup", disabled=True, use_container_width=True)

def page_four():
    st.header("Your plan is ready!")
    st.write("Let's create your first task!")

    if st.button("Proceed to Cadence", use_container_width=True):
        st.session_state.screen = "dashboard"
        st.session_state.redirect_to_dashboard = True
        st.rerun()

def onboarding():

    if st.session_state.page == 1:
        page_one()

    elif st.session_state.page == 2:
        page_two()

    elif st.session_state.page == 3:
        page_three()

    elif st.session_state.page == 4:
        page_four()
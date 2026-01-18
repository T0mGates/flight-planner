## Inspiration
The team was inspired this UOttaHack by a shared desire to build code that wasn't just beautiful or functional, but had a tangible impact on people's lives. Nav Canada's challenge was an opportunity to build a tool that could show real public benefit, and go beyond just maximizing a balance sheet.

## What it does
WingIt is able to visualize hundreds of flights at the same time as they complete a schedule. Watch planes depart airports, fly their course at any time, and complete their journey over the day. Then, run flight scheduling analysis to see what routes need to be changed to avoid close passes in the air within the minimum acceptable distance. With the proposed changes and original schedule side by side, make follow up questions with a Google Gemini agent to get the important details faster. Once the proposed changes are understood and accepted, apply them to resolve flight conflicts!

## How we built it
The team's tech stack was based around a Python + FastAPI backend along with a React + Vite + TypeScript frontend. The team also leveraged Sentry's error tracking, profiling, AI agent tracking, and traces on both the frontend and backend to help collect stats about our development and understand problems better.

The team started small and worked our way up. Our first versions weren't much more than a map and a couple crude images on the screen. 

Using continuous integration practices recommended by Martin Fowler himself to keep our development cycle super lightweight, we were able to consistently add feature after feature, component after component, and API endpoint after API endpoint. Eventually, almost magically, we were done!

## Challenges we ran into
Crunching numbers for thousands of flights isn't easy, and neither is displaying them. The team had problems with performance and optimization, but that just meant the team was able to put the skills we've been learning in our degrees to the test.

## Accomplishments that we're proud of
We're super proud of our scheduling optimizer, which can handle thousands of collisions and consider tens of different ways to optimize at the same time. We're also really proud of our AI integration, since we think the way it can augment a human operator's exercise and save them time is extremely valuable. Finally, we think we built a really beautiful interface. 
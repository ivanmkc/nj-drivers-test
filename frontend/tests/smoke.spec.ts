import { test, expect, type Page } from '@playwright/test';

// The happy path a first-time user takes, against the production build.
// Every selector is a role or visible text so the test survives styling
// changes; question content is data-driven and never asserted literally.

async function answerCurrentQuestion(page: Page) {
  // Choice buttons are labelled "A: <text>", "B: <text>", ...
  await page.getByRole('button', { name: /^A: / }).click();
  const next = page.getByRole('button', { name: /^(Next|See Results)$/ });
  await expect(next).toBeVisible();
  const label = await next.textContent();
  await next.click();
  return label?.trim() === 'See Results';
}

test('state index loads and the picker lists all 50 states', async ({ page }) => {
  await page.goto('./');
  await expect(page.getByRole('heading', { name: "Driver's Test Practice" })).toBeVisible();
  await expect(page.getByRole('button', { name: /New Jersey/ })).toBeEnabled();
  // DC has no bank yet and therefore no config.json, so exactly 50 cards.
  await expect(page.getByRole('button', { name: /questions$/ })).toHaveCount(50);
  // Legal pages are linked from the footer.
  await expect(page.getByRole('link', { name: 'Privacy' })).toHaveAttribute('href', /privacy\/$/);
});

test('pick a state, run a 10-question quiz, see results and stats', async ({ page }) => {
  await page.goto('./');
  await page.getByRole('button', { name: /New Jersey/ }).click();

  await expect(page.getByRole('button', { name: 'Start Quiz' })).toBeVisible();
  await page.getByRole('button', { name: '10', exact: true }).click();
  await page.getByRole('button', { name: 'Start Quiz' }).click();

  // The bank is fetched on demand; the first question must appear.
  await expect(page.getByRole('button', { name: /^A: / })).toBeVisible();

  let finished = false;
  for (let i = 0; i < 10 && !finished; i++) {
    finished = await answerCurrentQuestion(page);
  }
  expect(finished).toBe(true);

  await expect(page.getByText(/^\d+%$/)).toBeVisible();
  await expect(page.getByRole('button', { name: 'New Quiz' })).toBeVisible();

  await page.getByRole('button', { name: 'View Stats' }).click();
  await expect(page.getByText(/Quizzes/i).first()).toBeVisible();

  // Progress persisted: reload lands on the start screen of the saved state.
  await page.goto('./');
  await expect(page.getByRole('button', { name: 'Start Quiz' })).toBeVisible();
  await expect(page.getByText(/New Jersey/).first()).toBeVisible();
});

test('language switch loads the Spanish bank', async ({ page }) => {
  await page.goto('./');
  await page.getByRole('button', { name: /New Jersey/ }).click();
  await page.getByRole('button', { name: /Spanish/ }).click();
  await expect(page.getByRole('button', { name: /Comenzar|Iniciar|Empezar/ })).toBeVisible();
  await page.getByRole('button', { name: /Comenzar|Iniciar|Empezar/ }).click();
  await expect(page.getByRole('button', { name: /^A: / })).toBeVisible();
});

test('legal pages are served', async ({ page }) => {
  for (const path of ['about/', 'privacy/', 'support/']) {
    const res = await page.goto(`./${path}`);
    expect(res?.ok()).toBe(true);
    await expect(page.getByRole('heading', { level: 1 })).toBeVisible();
  }
  await expect(page.getByRole('link', { name: /Open Driver's Test Prep/ })).toHaveCount(0);
  const res = await page.goto('./data/index.json');
  expect(res?.ok()).toBe(true);
});

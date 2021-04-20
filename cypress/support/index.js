import 'cypress-axe'

const logA11yIssues = violations => {
  const violationData = violations.map(({ impact, help, nodes }) => ({
    impact,
    help,
    html: nodes[0].html,
  }))

  const docsLinks = violations.map(({ helpUrl }) => ({
    linkToDocs: helpUrl,
  }))

  cy.task('table', violationData)
  cy.task('table', docsLinks)
}

Cypress.Commands.add('runA11y', (context = null, options = null) => {
  cy.checkA11y(context, options, logA11yIssues)
})

// now any cookie with the name 'session_id' will
// not be cleared before each test runs
Cypress.Cookies.defaults({
  preserve: 'session_id',
})

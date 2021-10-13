import users from '../fixtures/user.json'
import govDepartments from '../fixtures/govDepartment.json'
import supplyChains from '../fixtures/supplyChains.json'
import umbrellas from '../fixtures/supplyChainUmbrellas.json'

const user = users[0].fields
const govDepartment = govDepartments[0].fields
const supplyChain = supplyChains.filter(sc => sc.fields.name === 'Supply Chain 5').map(sc => sc.fields)[0]

describe('The Supply Chain TaskComplete Page', () => {
  it('successfully loads', () => {
    cy.visit(Cypress.config('baseUrlSC') + `/${supplyChain.slug}/complete/`)
    cy.injectAxe()
  })
  it('has no accessibility issues', () => {
    cy.runA11y()
  })
  it("displays user's name and department in header", () => {
    cy.get('.app-header-item').should(
      'have.text',
      `${user.first_name} ${user.last_name} - ${govDepartment.name}`
    )
  })
  it('displays breadcrumbs', () => {
    cy.get('ol').children().should('have.length', 3)
    cy.get('li').contains('Home').should('have.attr', 'href').and('eq', '/')
    cy.get('li').contains('Monthly update').should('have.attr', 'href').and('eq', '/supply-chains/')
    cy.get('li')
      .contains(supplyChain.name)
      .should('have.attr', 'href')
      .and('eq', `/supply-chains/${supplyChain.slug}/`)
  })
  it('displays the correct text', () => {
    cy.get('h1').contains('Update complete')
    cy.get('div').contains(
      `Thank you for submitting your monthly update for the ${supplyChain.name} supply chain.`
    )
  })
  it('displays the correct inset text', () => {
    cy.get('h2 + p').invoke('text').should('match', /You have given updates for\s+\d+ of \d+ supply chains./)
  })
  it('displays the correct link back to home', () => {
    cy.get('p').contains(
      'You can go back and give an update for another supply chain.'
    )

    cy.get('#home').should('have.attr', 'href').and('equal', '/supply-chains/')
  })
})

const completedSC = supplyChains[1].fields

describe('Validate complete view for manual access', () => {
  it('successfully loads ready_to_submit Supply chain, by redirecting to tasklist page', () => {
    cy.visit(Cypress.config('baseUrlSC') + `/${completedSC.slug}/complete/`)
  })
  it('displays breadcrumbs', () => {
    cy.get('ol').children().should('have.length', 2)
    cy.get('li').contains('Home').should('have.attr', 'href').and('eq', '/')
    cy.get('li').contains('Monthly update').should('have.attr', 'href').and('eq', '/supply-chains/')
  })
  it('displays the correct header', () => {
    cy.get('h1').contains(`Update ${completedSC.name}`)
    cy.get('div').contains('Update complete')
    cy.get('div').contains('All actions are ready to be submitted.')
  })
  it('displays the correct table caption', () => {
    cy.get('caption').contains('Monthly strategic actions updates')
  })
  it('displays 2 strategic actions in the table', () => {
    cy.get('tbody').find('tr').should('have.length', 2)
    cy.get('tbody').find('td').should('have.length', 4)
    cy.get('td').contains('Ready to submit')
  })
  it('displays enabled submit button', () => {
    cy.get('form').find('button').should('be.enabled')
  })
})

const incompletedUmbrella = umbrellas.filter(u => u.fields.name === "Snacks").map(u => u.fields)[0]
const completeURL = Cypress.config('baseUrlSC') + `/${incompletedUmbrella.slug}/complete/`
const tasklistURL = Cypress.config('baseUrlSC') + `/${incompletedUmbrella.slug}/`

describe('Validate complete view on supply chain umbrella with manual access', () => {
  it('successfully loads by redirecting to tasklist page', () => {
    cy.visit(completeURL)
    cy.url().should('eq', tasklistURL)
  })
})

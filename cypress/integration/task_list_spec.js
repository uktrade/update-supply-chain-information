import users from '../fixtures/user.json'
import govDepartments from '../fixtures/govDepartment.json'
import supplyChains from '../fixtures/supplyChains.json'


const user = users[0].fields
const govDepartment = govDepartments[0].fields
const supplyChain = supplyChains[4].fields

describe('The Supply Chain Tasklist Page', () => {
  it('successfully loads', () => {
    cy.visit(Cypress.config('baseUrl') + `/${supplyChain.slug}`)
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
  it('displays bread crumbs', () => {
    cy.get('li').contains('Home')
    cy.get('li').contains(`Update ${supplyChain.name}`)
  })
  it('displays the correct header', () => {
    cy.get('h1').contains(`Update ${supplyChain.name}`)
    cy.get('div').contains(`Update complete`)
    cy.get('div').contains(`1 of 1 mandatory actions are complete.`)
  })
  it('displays correct table headers', () => {
    cy.get('thead').find('th').should('have.length', 2)
    cy.get('th').contains('Monthly strategic actions updates')
  })
  it('displays 1 strategic action in the table', () => {
    cy.get('tbody').find('tr').should('have.length', 1)
    cy.get('tbody').find('td').should('have.length', 2)
    cy.get('td').contains('submitted')
  })
  // it('displays enabled submit button', () => {
  //   cy.get('form').find('button').should('be.enabled')
  // })
})


const completedSC = supplyChains[1].fields

describe('Allowed to submit completed Supply Chains', () => {
  it('successfully loads', () => {
    cy.visit(Cypress.config('baseUrl') + `/${completedSC.slug}`)
  })
  it('displays the correct header', () => {
    cy.get('h1').contains(`Update ${completedSC.name}`)
    cy.get('div').contains(`Update complete`)
    cy.get('div').contains(`2 of 2 mandatory actions are complete.`)
  })
  it('displays 2 strategic action in the table', () => {
    cy.get('tbody').find('tr').should('have.length', 2)
    cy.get('tbody').find('td').should('have.length', 4)
    cy.get('td').contains('completed')
  })
  it('displays enabled submit button', () => {
    cy.get('form').find('button').should('be.enabled')
  })
  it.skip('can submit updates for supply chain', () => {
    cy.get('form').find('button').click()
    cy.url().should('eq', Cypress.config('baseUrl') + `/${completedSC.slug}/complete`)
    cy.get('li').contains('Home')
    cy.get('li').contains('Update complete')
  })
})

const largeSC = supplyChains[0].fields

describe('Paginate Strategic actions', () => {
  it('successfully loads', () => {
    cy.visit(Cypress.config('baseUrl') + `/${largeSC.slug}`)
  })
  it('displays 5 strategic actions in the table', () => {
    cy.get('tbody').find('tr').should('have.length', 5)
  })
  it('displays correct items in pagination list', () => {
    cy.get('.moj-pagination__list').find('li').should('have.length', 4)
    cy.get('.moj-pagination__item--active').contains('1')
    cy.get('.moj-pagination__item').contains('2')
    cy.get('.moj-pagination__item').contains('Next')
  })
  it('displays second page of strategic actions after clicking Next', () => {
    cy.contains('Next').click()
    cy.url().should('eq', Cypress.config('baseUrl') + `/${largeSC.slug}?page=2`)
    cy.get('tbody').find('tr').should('have.length', 2)
  })
  it('displays first page of strategic actions after clicking Previous', () => {
    cy.contains('Previous').click()
    cy.url().should('eq', Cypress.config('baseUrl') + `/${largeSC.slug}?page=1`)
  })
  it('displays enabled submit button', () => {
    cy.get('form').find('button').should('be.enabled')
  })
})
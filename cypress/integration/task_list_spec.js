import users from '../fixtures/user.json'
import govDepartments from '../fixtures/govDepartment.json'
import supplyChains from '../fixtures/supplyChains.json'

const user = users[0].fields
const govDepartment = govDepartments[0].fields
const supplyChain = supplyChains[0].fields

describe('The Supply Chain Tasklist Page', () => {
  it('successfully loads', () => {
    cy.visit(Cypress.config('baseUrlSC') + `/${supplyChain.slug}`)
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
    cy.get('ol').children().should('have.length', 2)
    cy.get('li').contains('Home').should('have.attr', 'href').and('eq', `/`)
    cy.get('li').contains('Monthly update').should('have.attr', 'href').and('eq', `/supply-chains/`)
  })
  it('displays the correct header', () => {
    cy.get('h1').contains(`Update ${supplyChain.name}`)
    cy.get('div').contains(`Update incomplete`)
    cy.get('div').contains('5 out of 7 actions are not ready to be submitted.')
  })
  it('displays the correct table caption', () => {
    cy.get('caption').contains('Monthly strategic actions updates')
  })
  it('displays 5 strategic action in the table', () => {
    cy.get('tbody').find('tr').should('have.length', 5)
    cy.get('tbody').find('td').should('have.length', 10)
    cy.get('td').contains('Not started')
  })
  it('displays enabled submit button', () => {
    cy.get('button').contains('Submit monthly update')
  })
})

const completedSC = supplyChains[1].fields

describe('Allowed to submit ready_to_submit Supply Chains', () => {
  it('successfully loads', () => {
    cy.visit(Cypress.config('baseUrlSC') + `/${completedSC.slug}`)
  })
  it('displays the correct header', () => {
    cy.get('h1').contains(`Update ${completedSC.name}`)
    cy.get('div').contains('Update complete')
    cy.get('div').contains('All actions are ready to be submitted.')
  })
  it('displays 2 strategic action in the table', () => {
    cy.get('tbody').find('tr').should('have.length', 2)
    cy.get('tbody').find('td').should('have.length', 4)
    cy.get('td').contains('Ready to submit')
  })
  it('displays enabled submit button', () => {
    cy.get('button').contains('Submit monthly update')
  })
  if (Cypress.env('RUNNING_LOCALLY') === '0') {
    // This test will only be run on CI or non-local environments as its un-safe operation
    // which alters state of objects(with the given fixtures)
    it('can submit updates for supply chain', () => {
      cy.get('form').find('button').click()
      cy.url().should(
        'eq',
        Cypress.config('baseUrlSC') + `/${completedSC.slug}/complete/`
      )
      cy.get('li').contains('Home')
      cy.get('li').contains('Update complete')
    })
  }
})

const submittedSC = supplyChains[4].fields

describe('Allowed to view submitted Supply chain', () => {
  it('successfully loads', () => {
    cy.visit(Cypress.config('baseUrlSC') + `/${submittedSC.slug}`)
  })
  it('displays the correct header with no action required', () => {
    cy.get('h1').contains(`Update ${submittedSC.name}`)
    cy.get('div').contains(`Update complete`).should('not.exist')
    cy.get('h2').contains('No action required')
    cy.get('p').contains(
      'You have already submitted the monthly update for this supply chain.'
    )
    cy.get('h2').contains('Before you submit').should('not.exist')
  })
  it('displays the correct table caption', () => {
    cy.get('caption').contains('Monthly strategic actions updates')
  })
  it('displays 1 strategic action in the table', () => {
    cy.get('tbody').find('tr').should('have.length', 1)
    cy.get('tbody').find('td').should('have.length', 2)
    cy.get('td').contains('Submitted')
  })
  it('displays strategic action name with hyperlink', () => {
    cy.get('td')
      .find('a')
      .invoke('text')
      .should('match', /Update .*$/)
    cy.get('td')
      .find('a')
      .should('have.attr', 'href')
      .and('match', /supply-chain-5.*/)
  })
  it('displays button to go back', () => {
    cy.get('a')
      .contains('Back')
      .should('have.attr', 'href')
      .and('equal', '/supply-chains/')
    cy.get('form').should('not.exist')
  })
})

const largeSC = supplyChains[0].fields

describe('Paginate Strategic actions', () => {
  it('successfully loads', () => {
    cy.visit(Cypress.config('baseUrlSC') + `/${largeSC.slug}`)
  })
  it('displays 5 strategic actions in the table', () => {
    cy.get('tbody').find('tr').should('have.length', 5)
  })
  it('displays correct items in pagination list', () => {
    cy.get('.moj-pagination__list').find('li').should('have.length', 3)
    cy.get('.moj-pagination__item--active').contains('1')
    cy.get('.moj-pagination__item').contains('2')
    cy.get('.moj-pagination__item').contains('Next')
  })
  it('displays second page of strategic actions after clicking Next', () => {
    cy.contains('Next').click()
    cy.url().should('eq', Cypress.config('baseUrlSC') + `/${largeSC.slug}/?page=2`)
    cy.get('tbody').find('tr').should('have.length', 2)
  })
  it('displays first page of strategic actions after clicking Previous', () => {
    cy.contains('Previous').click()
    cy.url().should('eq', Cypress.config('baseUrlSC') + `/${largeSC.slug}/?page=1`)
  })
  it('displays enabled submit button', () => {
    cy.get('button').contains('Submit monthly update')
  })
})

describe('Error handling while submitting incomplete updates', () => {
  it('successfully loads', () => {
    cy.visit(Cypress.config('baseUrlSC') + `/${largeSC.slug}`)
  })
  it('displays 5 strategic action in the table', () => {
    cy.get('tbody').find('tr').should('have.length', 5)
    cy.get('tbody').find('td').should('have.length', 10)
    cy.get('td').contains('Not started')
  })
  it('displays enabled submit button', () => {
    cy.get('form').find('button').should('be.enabled')
  })
  it('display error on submission', () => {
    cy.get('form').find('button').click()
    cy.url().should('eq', Cypress.config('baseUrlSC') + `/${largeSC.slug}/`)
    cy.get('#error-summary-title').contains('There is a problem')
    cy.get('li')
      .find('a')
      .contains('Updates must be given for all strategic actions')
      .should('have.attr', 'href')
      .and('equal', '#updates')
  })
})

import users from '../fixtures/user.json'
import govDepartments from '../fixtures/govDepartment.json'
import supplyChains from '../fixtures/supplyChains.json'
import { urlBuilder } from "../support/utils.js"

const adminUser = users[0].fields
const govDepartment = govDepartments[0].fields
const supplyChain = supplyChains[0]
const urls = urlBuilder(supplyChain);


describe('The SAP listing page', () => {
  it('successfully loads', () => {
    cy.visit(urls.sap)
    cy.injectAxe()
  })
  it('has no accessibility issues', () => {
    cy.runA11y()
  })
  it("displays user's name and department in header", () => {
    cy.get('.app-header-item').should(
      'have.text',
      `${adminUser.first_name} ${adminUser.last_name} - ${govDepartment.name}`
    )
  })
  it('displays the correct header', () => {
    cy.get('h1').contains(`Strategic action progress`)
    cy.get('p').contains(`Apply filters to see strategic action progress`)
  })
  it('can select department, supply chain and submit', () => {
    const successUrl = urls.sap + `${govDepartment.name}/` + `${supplyChain.fields.slug}/`
    cy.get('div > #id_department').select(`${govDepartment.name}`)
    cy.url().should('eq', urls.sap + `${govDepartment.name}/`)
    cy.get('div > #id_supply_chain').select(`${supplyChain.fields.name}`)
    cy.get('button').contains('Apply filters').click()
    cy.url().should('eq', successUrl)
  })
  it('expect sections within filtered results', () => {
    cy.get('h3').contains(`${govDepartment.name}`)
    cy.get('h2').contains(`${supplyChain.fields.name}`)
    cy.get('p').contains('Select a strategic action to view progress details and information')
    cy.get('a').contains(
      'Back to top'
    )
    cy.get('div.govuk-tabs ul.govuk-tabs__list').children().should('have.length', 2)
    cy.get('div.govuk-tabs ul.govuk-tabs__list li')
      .should('have.length', 2)
      .each(($el) => {
        cy.wrap($el).find('a').should('exist').contains(/[A, Ina]ctive strategic actions/)
        cy.wrap($el).find('a').should('have.attr', 'href').and('match', /[a,ina]ctive-actions/)
      })
    cy.get('div.govuk-tabs div.govuk-tabs__panel')
      .should('have.length', 2)
      .each(($el) => {
        cy.wrap($el).find('h3').should('exist').contains(/[A, Ina]ctive strategic actions/)
        cy.wrap($el).find('table.govuk-table tbody.govuk-table__body tr.govuk-table__row')
          .should('exist')
          .then(($row) => {
            cy.wrap($row).find('td.govuk-table__cell').should('exist')
              .each(($data) => {
                cy.wrap($data).find('a.govuk-link')
                  .should('exist')
                  .should('have.attr', 'href')
                cy.wrap($data).find('p.sap-action-description').should('exist')
              })
          })
      })
    cy.get('#active-actions').find('p.govuk-body').should('not.exist')
    cy.get('#inactive-actions').find('p.govuk-body').should('not.exist')
  })
})

const successUrl = urls.sap + `${govDepartment.name}/` + `${supplyChain.fields.slug}/`

describe('Pagination of SAP list', () => {
  it('successfully loads', () => {
    cy.visit(urls.sap)
  })
  it('can select department, supply chain and submit', () => {
    cy.get('div > #id_department').select(`${govDepartment.name}`)
    cy.url().should('eq', urls.sap + `${govDepartment.name}/`)
    cy.get('div > #id_supply_chain').select(`${supplyChain.fields.name}`)
    cy.get('button').contains('Apply filters').click()
    cy.url().should('eq', successUrl)
  })
  it('displays correct items in pagination list', () => {
    cy.get('.moj-pagination__list').find('li').should('have.length', 3)
    cy.get('.moj-pagination__item--active').contains('1')
    cy.get('.moj-pagination__item').contains('2')
    cy.get('.moj-pagination__item').contains('Next')
  })
  it('displays second page of strategic actions after clicking Next', () => {
    cy.contains('Next').click()
    cy.url().should('eq', successUrl + `?page=2`)
    cy.get('tbody').find('tr').should('have.length', 3)
  })
  it('displays first page of strategic actions after clicking Previous', () => {
    cy.contains('Previous').click()
    cy.url().should('eq', successUrl + `?page=1`)
  })
})

const emptySC = supplyChains.filter(sc => sc.fields.name === 'Supply Chain 3')[0]
const emptyListUrl = urls.sap + `${govDepartment.name}/` + `${emptySC.fields.slug}/`

describe('Describe supply chain with no strategic actions', () => {
  it('successfully loads', () => {
    cy.visit(emptyListUrl)
  })
  it('display correct content header', () => {
    cy.get('h3').contains(`${govDepartment.name}`)
    cy.get('h2').contains(`${emptySC.fields.name}`)
    cy.get('p').contains('Select a strategic action to view progress details and information')
  })
  it('displays empty actions message', () => {
    cy.get('#active-actions').find('h3.govuk-heading-m').should('not.exist')
    cy.get('#active-actions').find('p.govuk-body').should('exist').contains('No active strategic actions found.')

    cy.get('#inactive-actions').find('h3.govuk-heading-m').should('not.exist')
    cy.get('#inactive-actions').find('p.govuk-body').should('exist').contains('No inactive strategic actions found.')
  })

})
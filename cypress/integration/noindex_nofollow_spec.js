import users from '../fixtures/user.json'
import govDepartments from '../fixtures/govDepartment.json'

const user = users[0].fields
const govDepartment = govDepartments[0].fields

describe('The Home Page', () => {
    it('has a <meta name="robots" content="noindex, nofollow"> tag', () => {
        cy.visit(Cypress.config('baseUrl'));
        cy.get('html head meta[name="robots"][content="noindex, nofollow"]').should('exist');
    })
})

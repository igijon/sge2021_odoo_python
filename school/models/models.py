# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import secrets
import logging
import re

_logger = logging.getLogger(__name__)


class student(models.Model):
    _name = 'school.student'
    _description = 'Los alumnos'

    name = fields.Char(string="Nombre", readonly=False, required=True, help='Este es el nombre')
    birth_year = fields.Integer()
    dni = fields.Char(string="DNI")
    password = fields.Char(default=lambda p: secrets.token_urlsafe(12))

    description = fields.Text()
    inscription_date = fields.Datetime(default=lambda d: fields.Datetime.now())
    last_login = fields.Datetime()
    is_student = fields.Boolean()
    level = fields.Selection([('1','Primero'),('2','Segundo')])
    photo = fields.Image(max_width=300, max_height=300) # Field binario pero específico para imágenes.
    classroom = fields.Many2one('school.classroom', domain="[('level','=',level)]", ondelete='set null', help='Clase a la que pertenece')
    teachers = fields.Many2many('school.teacher', related='classroom.teachers', readonly=True)
    state = fields.Selection([('1', 'Matriculado'), ('2', 'Estudiante'), ('3', 'Ex-estudiante')], default="1")
    @api.constrains('dni')
    def _check_dni(self):
        regex = re.compile('[0-9]{8}[a-z]\Z', re.I)
        for student in self:
            #Ahora vamos a validar si se cumple la condición
            if not regex.match(student.dni):
                #No coinciden por lo que tenemos que informar e impedir que se guarde
                raise ValidationError('DNI format incorrect')

    _sql_constraints = [('dni_uniq','unique(dni)','DNI can\'t be repeated')]

    # También recibe un recordset
    def regenerate_password(self):
        for student in self:
            pw = secrets.token_urlsafe(12)
            student.write({'password':pw})


class classroom(models.Model):
    _name = 'school.classroom'
    _description = 'Las clases'

    name = fields.Char() # Todos los modelos deben tener un field name
    level = fields.Selection([('1','1'),('2','2')])
    students = fields.One2many(string='Alumnos', comodel_name='school.student', inverse_name='classroom')
    teachers = fields.Many2many(comodel_name='school.teacher',
                                relation='teachers_classroom',
                                column1='classroom_id',
                                column2='teacher_id')
    teachers_last_year = fields.Many2many(comodel_name='school.teacher',
                                relation='teachers_classroom_ly',
                                column1='classroom_id',
                                column2='teacher_id')
    # Vamos a considerar para el ejemplo que una clase puede tener un coordinador (profesor) y que un mismo profesor
    # pudiera ser coordinador de varias clases
    coordinator = fields.Many2one('school.teacher', compute='_get_coordinator')

    all_teachers = fields.Many2many('school.teacher', compute='_get_teacher')

    def _get_coordinator(self):
        for classroom in self:
            if len(classroom.teachers) > 0:
                classroom.coordinator = classroom.teachers[0].id #Para el ejemplo, vamos a establecer como coordinador al primero de la lista
            else:
                classroom.coordinator = None

    def _get_teacher(self):
        for classroom in self:
            # Para trabajar, acepta o lista de id o recordset, las dos cosas le valen. En este caso le metemos recordset.
            classroom.all_teachers = classroom.teachers + classroom.teachers_last_year

class teacher(models.Model):
    _name = 'school.teacher'
    _description = 'Los profesores'

    name = fields.Char()  # Todos los modelos deben tener un field name
    topic = fields.Char()
    phone = fields.Char()

    classrooms = fields.Many2many(comodel_name='school.classroom',
                                  relation='teachers_classroom',
                                  column1='teacher_id',
                                  column2='classroom_id')
    classrooms_last_year = fields.Many2many(comodel_name='school.classroom',
                                  relation='teachers_classroom_ly',
                                  column1='teacher_id',
                                  column2='classroom_id')

class seminar(models.Model):
    _name = 'school.seminar'
    name = fields.Char()
    date = fields.Datetime()
    finish = fields.Datetime()
    hours = fields.Integer()
    classroom = fields.Many2one('school.classroom')


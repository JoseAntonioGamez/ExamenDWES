from django import forms
from django.forms import ModelForm
from datetime import date
from .models import Usuario, Paciente, Investigador, Farmaco, EnsayoClinico
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group


class RegistroForm(UserCreationForm):
	roles = (
		(Usuario.PACIENTE, 'Paciente'),
		(Usuario.INVESTIGADOR, 'Investigador'),
	)
	rol = forms.ChoiceField(choices=roles)
	edad = forms.IntegerField(min_value=0, required=False, label="Edad (solo para pacientes)")
	ciudad = forms.CharField(required=False, max_length=50, label="Ciudad (solo investigadores)")
	telefono = forms.CharField(required=False, max_length=15, label="Teléfono (solo pacientes)")

	class Meta:
		model = Usuario
		fields = ['username', 'email', 'rol', 'password1', 'password2', 'ciudad', 'telefono']

	def clean(self):
		cleaned_data = super().clean()
		rol = cleaned_data.get('rol')
		ciudad = cleaned_data.get('ciudad')
		telefono = cleaned_data.get('telefono')

		# En este proyecto interpretamos: investigadors deben proporcionar ciudad, pacientes teléfono
		if rol and int(rol) == Usuario.INVESTIGADOR and not ciudad:
			self.add_error('ciudad', 'La ciudad es obligatoria para investigadores.')

		if rol and int(rol) == Usuario.PACIENTE and not telefono:
			self.add_error('telefono', 'El teléfono es obligatorio para pacientes.')

		return cleaned_data


class RegistroPacienteForm(UserCreationForm):
	edad = forms.IntegerField(min_value=18, label="Edad (mayor de 18)")

	class Meta:
		model = Usuario
		fields = ('username', 'email', 'password1', 'password2', 'edad')

	def save(self, commit=True, grupo='Pacientes'):
		user = super().save(commit=False)
		user.rol = Usuario.PACIENTE
		if commit:
			user.save()
			group, _ = Group.objects.get_or_create(name=grupo)
			group.user_set.add(user)

			edad = self.cleaned_data.get('edad')
			fecha_nacimiento = None
			if edad is not None:
				today = date.today()
				try:
					fecha_nacimiento = date(today.year - int(edad), today.month, today.day)
				except ValueError:
					fecha_nacimiento = date(today.year - int(edad), today.month, min(today.day, 28))

			Paciente.objects.create(usuario=user, edad=edad, nombre=user.username, fecha_nacimiento=fecha_nacimiento)
		return user


class RegistroInvestigadorForm(UserCreationForm):
	class Meta:
		model = Usuario
		fields = ('username', 'email', 'password1', 'password2')

	def save(self, commit=True, grupo='Investigadores'):
		user = super().save(commit=False)
		user.rol = Usuario.INVESTIGADOR
		if commit:
			user.save()
			group, _ = Group.objects.get_or_create(name=grupo)
			group.user_set.add(user)
			Investigador.objects.create(usuario=user, nombre=user.username)
		return user


class InvestigadorForm(ModelForm):
	class Meta:
		model = Investigador
		fields = ['nombre', 'especialidad', 'afiliacion_institucional']
		labels = {
			'nombre': 'Nombre completo del investigador',
			'especialidad': 'Especialidad',
			'afiliacion_institucional': 'Afiliación institucional',
		}

	def clean_nombre(self):
		nombre = self.cleaned_data.get('nombre')
		if not nombre:
			return nombre
		if len(nombre) > 100:
			self.add_error('nombre', 'El nombre no puede superar 100 caracteres.')

		qs = Investigador.objects.filter(nombre__iexact=nombre)
		if self.instance.pk:
			qs = qs.exclude(pk=self.instance.pk)
		if qs.exists():
			self.add_error('nombre', 'Ya existe un investigador con ese nombre.')
		return nombre


class EnsayoClinicoForm(ModelForm):
	class Meta:
		model = EnsayoClinico
		fields = ['nombre', 'descripcion', 'farmaco', 'pacientes', 'nivel_seguimiento', 'fecha_inicio', 'fecha_fin', 'activo']
		widgets = {
			'descripcion': forms.Textarea(attrs={'rows': 4}),
			'pacientes': forms.SelectMultiple(),
			'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
			'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
		}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['farmaco'].queryset = Farmaco.objects.filter(apto_para_ensayos=True)

	def clean_nombre(self):
		nombre = self.cleaned_data.get('nombre')
		if nombre:
			if len(nombre) > 80:
				self.add_error('nombre', 'El nombre no puede superar 80 caracteres.')
			qs = EnsayoClinico.objects.filter(nombre__iexact=nombre)
			if self.instance.pk:
				qs = qs.exclude(pk=self.instance.pk)
			if qs.exists():
				self.add_error('nombre', 'Ya existe un ensayo con ese nombre.')
		return nombre

	def clean_descripcion(self):
		descripcion = self.cleaned_data.get('descripcion', '')
		if len(descripcion or '') < 100:
			self.add_error('descripcion', 'Debe tener al menos 100 caracteres')
		return descripcion

	def clean_pacientes(self):
		pacientes = self.cleaned_data.get('pacientes')
		if pacientes:
			for p in pacientes:
				if p.edad is not None and p.edad < 18:
					self.add_error('pacientes', 'Todos los pacientes deben ser mayores de edad')
					break
		return pacientes

	def clean(self):
		cleaned = super().clean()
		fecha_inicio = cleaned.get('fecha_inicio')
		fecha_fin = cleaned.get('fecha_fin')

		if fecha_inicio and fecha_fin and fecha_inicio >= fecha_fin:
			self.add_error('fecha_inicio', 'Fecha inicio debe ser anterior a fecha fin')

		if not (self.instance and self.instance.pk) and fecha_fin and fecha_fin < date.today():
			self.add_error('fecha_fin', 'Fecha fin debe ser igual o posterior a hoy')

		return cleaned

	def save(self, commit=True, usuario=None):
		ensayo = super().save(commit=False)
		if usuario is not None:
			investigador = Investigador.objects.filter(usuario=usuario).first()
			if investigador:
				ensayo.creado_por = investigador
		if commit:
			ensayo.save()
			self.save_m2m()
		return ensayo


class BusquedaAvanzadaEnsayoForm(forms.Form):
	textoBusqueda = forms.CharField(required=False, label="Texto (nombre/descripción)")
	fecha_inicio_desde = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}), label="Fecha inicio desde")
	fecha_inicio_hasta = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}), label="Fecha inicio hasta")
	nivel_seguimiento_min = forms.IntegerField(required=False, min_value=0, max_value=10, label="Nivel seguimiento mayor que")
	pacientes = forms.ModelMultipleChoiceField(queryset=Paciente.objects.all(), required=False)
	solo_activos = forms.BooleanField(required=False, label="Solo ensayos activos")


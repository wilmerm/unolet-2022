import smtplib 
 


class EmailException(Exception):

    def __init__(self, message="Email error"):
        self.message = message



class Email(object):

    def Send(self, from_name, from_email, to_name, to_email, subject, message):
        """
        Envia un correo electrónico.

        parámetros:
            from_name: nombre del remitente.
            from_email: correo electrónico del remitente.
            to_name: nombre del destinatario.
            to_email: correo electrónico del destinatario.
            subject: asunto del mensaje.
            message: texto del mensaje.

        return bool
        """
        email = self.GetTemplate(from_name, from_email, to_name, to_email, subject, message)
        try: 
            smtp = smtplib.SMTP('localhost') 
            smtp.sendmail(from_email, to_email, email) 
            return True
        except BaseException as e: 
            raise EmailException("Error enviando el mensaje. {}".format(e.message))


    def GetTemplate(self, from_name, from_email, to_name, to_email, subject, message):
        return """From: {} <{}> 
                  To: {} <{}> 
                  MIME-Version: 1.0 
                  Content-type: text/html 
                  Subject: {} 

                  {}
                   """.format(from_name, from_email, to_name, to_email, subject, message)